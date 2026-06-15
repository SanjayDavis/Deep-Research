use serde::{Deserialize, Serialize};

// ── Data types ──────────────────────────────────────────────

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct ReportMeta {
    pub path: String,
    pub filename: String,
    pub title: String,
    pub date: String,
    pub word_count: u32,
    pub source_count: u32,
    pub rounds: u32,
    pub depth: u32,
    pub session_id: String,
}

#[derive(Debug, Clone, Default, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct ProviderConfig {
    pub r#type: String,
    pub label: String,
    pub base_url: String,
    pub api_key: String,
    pub model: String,
    pub models: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
    #[serde(rename_all = "camelCase")]
    pub struct AppSettings {
    pub provider: String,
    pub providers: std::collections::HashMap<String, ProviderConfig>,
    #[serde(default)]
    pub searxng_url: String,
    pub theme: String,
    pub research_depth: u32,
    pub max_pages_per_query: u32,
    pub num_rounds: u32,
    pub time_limit_minutes: u32,
}

impl Default for AppSettings {
    fn default() -> Self {
        let mut providers = std::collections::HashMap::new();
        providers.insert("openrouter".into(), ProviderConfig {
            r#type: "openrouter".into(),
            label: "OpenRouter".into(),
            base_url: "https://openrouter.ai/api/v1".into(),
            api_key: String::new(),
            model: "google/gemini-2.0-flash-001".into(),
            models: vec![],
        });
        providers.insert("lm-studio".into(), ProviderConfig {
            r#type: "lm-studio".into(),
            label: "LM Studio".into(),
            base_url: "http://localhost:1234/v1".into(),
            api_key: String::new(),
            model: String::new(),
            models: vec![],
        });
        providers.insert("opencode-proxy".into(), ProviderConfig {
            r#type: "opencode-proxy".into(),
            label: "OpenCode Proxy".into(),
            base_url: "http://127.0.0.1:4010/v1".into(),
            api_key: String::new(),
            model: String::new(),
            models: vec![],
        });
        Self {
            provider: "openrouter".into(),
            providers,
            searxng_url: String::new(),
            theme: "dark".into(),
            research_depth: 3,
            max_pages_per_query: 25,
            num_rounds: 2,
            time_limit_minutes: 30,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct ProgressPayload {
    pub r#type: String,
    pub stage: Option<String>,
    pub message: String,
    pub pct: Option<u32>,
    pub subtask: Option<String>,
    pub round: Option<u32>,
    #[serde(rename = "roundTotal")]
    pub round_total: Option<u32>,
    pub elapsed: Option<f64>,
    pub data: Option<serde_json::Value>,
}

impl ProgressPayload {
    pub fn error(message: impl Into<String>) -> Self {
        Self {
            r#type: "error".into(),
            stage: None,
            message: message.into(),
            pct: None,
            subtask: None,
            round: None,
            round_total: None,
            elapsed: None,
            data: None,
        }
    }

    pub fn cancelled() -> Self {
        Self {
            r#type: "cancelled".into(),
            stage: None,
            message: "Research cancelled".into(),
            pct: None,
            subtask: None,
            round: None,
            round_total: None,
            elapsed: None,
            data: None,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct ResearchSession {
    pub running: bool,
    pub topic: String,
}

// ── Application state ───────────────────────────────────────

pub struct AppState {
    pub settings: std::sync::Mutex<AppSettings>,
    pub research: std::sync::Mutex<ResearchSession>,
    pub process: std::sync::Mutex<Option<std::process::Child>>,
    pub cancelled: std::sync::Mutex<bool>,
}
