use std::io::{BufRead, BufReader};
use std::path::PathBuf;
use std::process::{Child, Stdio};
use tauri::{AppHandle, Emitter, Manager, State};
use serde::{Deserialize, Serialize};

use crate::models::{AppSettings, ProgressPayload, ResearchSession};
use crate::settings::save_settings_to_disk;

fn find_python() -> PathBuf {
    if let Ok(cwd) = std::env::current_dir() {
        for rel in [".venv/bin/python3", ".venv/Scripts/python.exe", "../.venv/bin/python3", "../../.venv/bin/python3"] {
            let p = cwd.join(rel);
            if p.exists() {
                return p;
            }
        }
    }
    if let Ok(exe) = std::env::current_exe() {
        if let Some(parent) = exe.parent() {
            for rel in [
                "../.venv/bin/python3", 
                ".venv/bin/python3",
                "../../.venv/bin/python3",
                "../../../.venv/bin/python3",
                "../../../.venv/Scripts/python.exe"
            ] {
                let p = parent.join(rel);
                if p.exists() {
                    return p;
                }
            }
        }
    }
    if let Ok(venv) = std::env::var("VIRTUAL_ENV") {
        let p = PathBuf::from(venv).join("bin/python3");
        if p.exists() {
            return p;
        }
    }
    PathBuf::from(if cfg!(target_os = "windows") {
        "python"
    } else {
        "python3"
    })
}

fn find_backend_dir(app: &AppHandle) -> Option<PathBuf> {
    let candidates: Vec<PathBuf> = [
        std::env::current_dir().ok().map(|d| d.join("backend")),
        app.path().resource_dir().ok().map(|d| d.join("backend")),
        std::env::current_exe()
            .ok()
            .and_then(|exe| exe.parent().map(|p| p.join("backend"))),
        std::env::current_exe()
            .ok()
            .and_then(|exe| exe.parent().map(|p| p.join("../backend"))),
        // Resolve symlinks (e.g. ~/.local/bin/deep-research -> project/src-tauri/target/...)
        std::env::current_exe()
            .ok()
            .and_then(|exe| std::fs::canonicalize(&exe).ok())
            .and_then(|exe| exe.parent().map(|p| p.join("../backend"))),
        std::env::current_exe()
            .ok()
            .and_then(|exe| std::fs::canonicalize(&exe).ok())
            .and_then(|exe| exe.parent().map(|p| p.join("backend"))),
    ]
    .into_iter()
    .flatten()
    .collect();

    for dir in candidates {
        if dir.join("main.py").exists() {
            return dir.canonicalize().ok().or(Some(dir));
        }
    }
    None
}

fn emit_payload(app: &AppHandle, payload: ProgressPayload) {
    let _ = app.emit("research-event", payload);
}

fn emit_error(app: &AppHandle, message: impl Into<String>) {
    emit_payload(app, ProgressPayload::error(message));
}

fn mark_research_stopped(app: &AppHandle) {
    let s = app.state::<crate::AppState>();
    let mut r = s.research.lock().unwrap();
    r.running = false;
}

// ── Research execution ──────────────────────────────────────

#[tauri::command]
pub async fn fetch_models(base_url: String, api_key: String) -> Result<Vec<String>, String> {
    let client = reqwest::Client::builder()
        .timeout(std::time::Duration::from_secs(10))
        .build()
        .map_err(|e| format!("Failed to create HTTP client: {}", e))?;

    let models_url = format!("{}/models", base_url.trim_end_matches('/'));

    let mut req = client.get(&models_url);
    if !api_key.is_empty() {
        req = req.header("Authorization", format!("Bearer {}", api_key));
    }

    let is_lm_studio = base_url.contains("localhost") || base_url.contains("127.0.0.1");

    let resp = req.send().await.map_err(|e| {
        if is_lm_studio {
            "Could not connect to LM Studio. Make sure LM Studio is running on port 1234 and has a model loaded.".into()
        } else {
            format!("Connection failed: {}. Is the server running?", e)
        }
    })?;

    let body: serde_json::Value = resp.json().await.map_err(|e| {
        if is_lm_studio {
            format!("LM Studio returned an unexpected response: {}. Try restarting LM Studio.", e)
        } else {
            format!("Parse failed: {}", e)
        }
    })?;

    let models = body["data"]
        .as_array()
        .ok_or("Unexpected API response format. Expected a 'data' array with model objects.")?;

    let ids: Vec<String> = models
        .iter()
        .filter_map(|m| m["id"].as_str().map(String::from))
        .collect();

    if ids.is_empty() {
        return Err(if is_lm_studio {
            "LM Studio returned no models. Make sure you have loaded a model in LM Studio (select a model file and click 'Start Server').".into()
        } else {
            "No models returned. Check that your provider is running and accessible.".into()
        });
    }

    Ok(ids)
}

#[tauri::command]
pub fn start_research(
    topic: String,
    settings: AppSettings,
    state: State<crate::AppState>,
    app: AppHandle,
) -> Result<(), String> {
    let mut research = state.research.lock().unwrap();
    if research.running {
        return Err("Research already in progress".into());
    }
    *research = ResearchSession {
        running: true,
        topic: topic.clone(),
    };
    drop(research);

    *state.cancelled.lock().unwrap() = false;
    *state.settings.lock().unwrap() = settings.clone();
    save_settings_to_disk(&app, &settings);

    let provider = settings
        .providers
        .get(&settings.provider)
        .cloned()
        .unwrap_or_default();

    if provider.model.trim().is_empty() {
        mark_research_stopped(&app);
        return Err("No model selected. Go to Settings, connect to your provider, and select a model.".into());
    }

    if settings.provider == "openrouter" && provider.api_key.trim().len() < 8 {
        mark_research_stopped(&app);
        return Err("OpenRouter requires an API key. Add your key in Settings and save.".into());
    }

    let app_handle = app.clone();
    let topic_clone = topic.clone();

    tauri::async_runtime::spawn(async move {
        let backend_dir = find_backend_dir(&app_handle);
        let python = find_python();

        let mut cmd = std::process::Command::new(&python);
        cmd.arg("-u").arg("main.py").arg(&topic_clone);

        cmd.arg("--provider").arg(&provider.r#type);
        cmd.arg("--base-url").arg(&provider.base_url);
        cmd.arg("--model").arg(&provider.model);

        if !provider.api_key.is_empty() {
            cmd.arg("--api-key").arg(&provider.api_key);
        }

        cmd.arg("--depth")
            .arg(settings.research_depth.to_string());
        cmd.arg("--rounds")
            .arg(settings.num_rounds.to_string());
        cmd.arg("--max-pages")
            .arg(settings.max_pages_per_query.to_string());
        cmd.arg("--time-limit")
            .arg(settings.time_limit_minutes.to_string());

        if !settings.searxng_url.is_empty() {
            cmd.arg("--searxng-url").arg(&settings.searxng_url);
        }

        if let Some(ref dir) = backend_dir {
            cmd.current_dir(dir);
        } else {
            emit_error(
                &app_handle,
                "Backend directory not found. Ensure backend/ exists next to the application.",
            );
            mark_research_stopped(&app_handle);
            return;
        }

        cmd.stdout(Stdio::piped());
        cmd.stderr(Stdio::piped());

        let mut child: Child = match cmd.spawn() {
            Ok(c) => c,
            Err(e) => {
                emit_error(
                    &app_handle,
                    format!(
                        "Failed to start backend ({}): {}. Run setup.sh or pip install -r backend/requirements.txt",
                        python.display(),
                        e
                    ),
                );
                mark_research_stopped(&app_handle);
                return;
            }
        };

        let stderr = child.stderr.take();
        let stdout = child.stdout.take().unwrap();

        {
            let state_ref = app_handle.state::<crate::AppState>();
            *state_ref.process.lock().unwrap() = Some(child);
        }

        if let Some(stderr) = stderr {
            let app_err = app_handle.clone();
            std::thread::spawn(move || {
                let reader = BufReader::new(stderr);
                for line in reader.lines() {
                    if let Ok(line) = line {
                        let trimmed = line.trim();
                        if trimmed.is_empty() {
                            continue;
                        }
                        emit_payload(
                            &app_err,
                            ProgressPayload {
                                r#type: "log".into(),
                                stage: None,
                                message: trimmed.to_string(),
                                pct: None,
                                subtask: None,
                                round: None,
                                round_total: None,
                                elapsed: None,
                                data: None,
                            },
                        );
                    }
                }
            });
        }

        let reader = BufReader::new(stdout);
        for line in reader.lines() {
            if let Ok(line) = line {
                if line.trim().is_empty() {
                    continue;
                }
                if let Ok(payload) = serde_json::from_str::<ProgressPayload>(&line) {
                    emit_payload(&app_handle, payload);
                }
            }
        }

        let was_cancelled = *app_handle.state::<crate::AppState>().cancelled.lock().unwrap();

        {
            let state_ref = app_handle.state::<crate::AppState>();
            let mut guard = state_ref.process.lock().unwrap();
            if let Some(mut child) = guard.take() {
                let _ = child.wait();
            }
        }

        if was_cancelled {
            emit_payload(&app_handle, ProgressPayload::cancelled());
        }

        mark_research_stopped(&app_handle);
    });

    Ok(())
}

#[tauri::command]
pub fn cancel_research(state: State<crate::AppState>, app: AppHandle) {
    *state.cancelled.lock().unwrap() = true;
    let mut proc = state.process.lock().unwrap();
    if let Some(ref mut child) = *proc {
        let _ = child.kill();
        let _ = child.wait();
    }
    *proc = None;
    let mut r = state.research.lock().unwrap();
    r.running = false;
    drop(r);
    emit_payload(&app, ProgressPayload::cancelled());
}
