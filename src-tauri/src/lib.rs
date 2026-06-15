mod commands;
mod models;
mod settings;

use tauri::Manager;

use crate::models::{AppSettings, AppState, ResearchSession};
use crate::commands::{reports, research, settings as settings_cmd};

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .manage(AppState {
            settings: std::sync::Mutex::new(AppSettings::default()),
            research: std::sync::Mutex::new(ResearchSession {
                running: false,
                topic: String::new(),
            }),
            process: std::sync::Mutex::new(None),
            cancelled: std::sync::Mutex::new(false),
        })
        .invoke_handler(tauri::generate_handler![
            settings_cmd::get_settings,
            settings_cmd::save_settings,
            settings_cmd::get_research_state,
            research::fetch_models,
            reports::get_report_content,
            reports::list_reports,
            reports::delete_report,
            reports::search_reports,
            reports::open_reports_folder,
            research::start_research,
            research::cancel_research,
        ])
        .setup(|app| {
            let handle = app.handle();
            let settings = crate::settings::load_settings(handle);
            *handle.state::<AppState>().settings.lock().unwrap() = settings;
            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
