use std::path::PathBuf;
use tauri_plugin_opener::OpenerExt;
use crate::models::ReportMeta;

// ── Reports directory ───────────────────────────────────────

pub fn reports_dir() -> PathBuf {
    let home = std::env::var("HOME").unwrap_or_else(|_| ".".into());
    PathBuf::from(home).join("deep_research_reports")
}

fn extract_frontmatter(content: &str, key: &str) -> Option<String> {
    let lines: Vec<&str> = content.lines().collect();
    let mut in_frontmatter = false;
    for line in lines {
        let trimmed = line.trim();
        if trimmed == "---" {
            if in_frontmatter {
                break;
            }
            in_frontmatter = true;
            continue;
        }
        if in_frontmatter {
            if let Some((k, v)) = trimmed.split_once(':') {
                if k.trim() == key {
                    return Some(v.trim().trim_matches('"').to_string());
                }
            }
        }
    }
    None
}

pub fn parse_report_meta(path: &PathBuf) -> Option<ReportMeta> {
    let content = std::fs::read_to_string(path).ok()?;
    let filename = path.file_name()?.to_string_lossy().to_string();
    
    // Extract frontmatter
    let title = extract_frontmatter(&content, "title").unwrap_or(filename.clone());
    let date = extract_frontmatter(&content, "date").unwrap_or_else(|| {
        let meta = std::fs::metadata(path);
        match meta {
            Ok(m) => match m.modified() {
                Ok(t) => match t.duration_since(std::time::UNIX_EPOCH) {
                    Ok(d) => d.as_secs().to_string(),
                    Err(_) => String::new(),
                },
                Err(_) => String::new(),
            },
            Err(_) => String::new(),
        }
    });
    let depth = extract_frontmatter(&content, "depth").and_then(|s| s.parse().ok()).unwrap_or(0);
    let rounds = extract_frontmatter(&content, "rounds").and_then(|s| s.parse().ok()).unwrap_or(0);
    let sources = extract_frontmatter(&content, "sources").and_then(|s| s.parse().ok()).unwrap_or(0);
    let _chunks = extract_frontmatter(&content, "chunks").and_then(|s| s.parse().ok()).unwrap_or(0);
    let session_id = extract_frontmatter(&content, "session_id").unwrap_or_default();
    
    let word_count = content.split_whitespace().count() as u32;
    let source_count = sources;
    
    Some(ReportMeta {
        path: path.to_string_lossy().to_string(),
        filename,
        title,
        date,
        word_count,
        source_count,
        rounds,
        depth,
        session_id,
    })
}

// ── Tauri commands ──────────────────────────────────────────

#[tauri::command]
pub fn list_reports() -> Result<Vec<ReportMeta>, String> {
    let dir = reports_dir();
    if !dir.exists() {
        return Ok(vec![]);
    }
    let mut reports: Vec<ReportMeta> = std::fs::read_dir(&dir)
        .map_err(|e| format!("Failed to read reports dir: {}", e))?
        .filter_map(|e| e.ok())
        .filter(|e| e.path().extension().map_or(false, |ext| ext == "md"))
        .filter_map(|e| parse_report_meta(&e.path()))
        .collect();
    reports.sort_by(|a, b| b.date.cmp(&a.date));
    Ok(reports)
}

#[tauri::command]
pub fn delete_report(path: String) -> Result<(), String> {
    std::fs::remove_file(&path).map_err(|e| format!("Failed to delete report: {}", e))
}

#[tauri::command]
pub fn search_reports(query: String) -> Result<Vec<ReportMeta>, String> {
    let dir = reports_dir();
    if !dir.exists() {
        return Ok(vec![]);
    }
    let q = query.to_lowercase();
    let mut reports: Vec<ReportMeta> = std::fs::read_dir(&dir)
        .map_err(|e| format!("Failed to read reports dir: {}", e))?
        .filter_map(|e| e.ok())
        .filter(|e| e.path().extension().map_or(false, |ext| ext == "md"))
        .filter_map(|e| parse_report_meta(&e.path()))
        .filter(|r| {
            r.title.to_lowercase().contains(&q)
                || r.filename.to_lowercase().contains(&q)
                || r.session_id.to_lowercase().contains(&q)
        })
        .collect();
    reports.sort_by(|a, b| b.date.cmp(&a.date));
    Ok(reports)
}

#[tauri::command]
pub fn get_report_content(path: String) -> Result<String, String> {
    std::fs::read_to_string(&path).map_err(|e| format!("Failed to read report: {}", e))
}

#[tauri::command]
pub fn open_reports_folder(app: tauri::AppHandle) -> Result<(), String> {
    let dir = reports_dir();
    if !dir.exists() {
        std::fs::create_dir_all(&dir).map_err(|e| format!("Failed to create reports dir: {}", e))?;
    }
    app.opener()
        .open_path(dir.to_string_lossy(), None::<&str>)
        .map_err(|e| format!("Failed to open folder: {}", e))
}