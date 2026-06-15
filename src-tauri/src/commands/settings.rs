use tauri::{AppHandle, State};

use crate::models::{AppSettings, ResearchSession};
use crate::settings::{load_settings, save_settings_to_disk};

#[tauri::command]
pub fn get_settings(state: State<crate::AppState>, app: AppHandle) -> AppSettings {
    let settings = load_settings(&app);
    *state.settings.lock().unwrap() = settings.clone();
    settings
}

#[tauri::command]
pub fn save_settings(state: State<crate::AppState>, app: AppHandle, settings: AppSettings) {
    save_settings_to_disk(&app, &settings);
    *state.settings.lock().unwrap() = settings;
}

#[tauri::command]
pub fn get_research_state(state: State<crate::AppState>) -> ResearchSession {
    state.research.lock().unwrap().clone()
}
