use std::path::PathBuf;
use tauri::{AppHandle, Manager};
use base64::{engine::general_purpose::STANDARD as BASE64, Engine as _};

use crate::models::AppSettings;

// Simple XOR encryption for API keys (better than plaintext)
fn encrypt_key(key: &str) -> String {
    if key.is_empty() {
        return String::new();
    }
    let salt = b"deep_research_salt_2024";
    let mut result = Vec::with_capacity(key.len());
    for (i, b) in key.bytes().enumerate() {
        result.push(b ^ salt[i % salt.len()]);
    }
    BASE64.encode(&result)
}

fn decrypt_key(encrypted: &str) -> String {
    if encrypted.is_empty() {
        return String::new();
    }
    let salt = b"deep_research_salt_2024";
    let bytes = BASE64.decode(encrypted).unwrap_or_default();
    let mut result = Vec::with_capacity(bytes.len());
    for (i, b) in bytes.iter().enumerate() {
        result.push(b ^ salt[i % salt.len()]);
    }
    String::from_utf8(result).unwrap_or_default()
}

// ── Settings file path ──────────────────────────────────────

pub fn settings_path(app: &AppHandle) -> PathBuf {
    let dir = app.path().app_data_dir().unwrap_or_else(|_| PathBuf::from("."));
    std::fs::create_dir_all(&dir).ok();
    dir.join("settings.json")
}

pub fn load_settings(app: &AppHandle) -> AppSettings {
    let path = settings_path(app);
    println!("Loading settings from: {:?}", path);
    if let Ok(data) = std::fs::read_to_string(&path) {
        println!("Settings file found, reading...");
        let mut settings: AppSettings = serde_json::from_str(&data).unwrap_or_else(|e| {
            println!("Failed to parse settings: {}", e);
            AppSettings::default()
        });
        // Decrypt API keys
        for (_, provider) in settings.providers.iter_mut() {
            if !provider.api_key.is_empty() {
                provider.api_key = decrypt_key(&provider.api_key);
            }
        }
        settings
    } else {
        println!("Settings file not found, using defaults.");
        AppSettings::default()
    }
}

pub fn save_settings_to_disk(app: &AppHandle, settings: &AppSettings) {
    let path = settings_path(app);
    println!("Saving settings to: {:?}", path);
    // Encrypt API keys before saving
    let mut settings_clone = settings.clone();
    for (_, provider) in settings_clone.providers.iter_mut() {
        if !provider.api_key.is_empty() {
            provider.api_key = encrypt_key(&provider.api_key);
        }
    }
    if let Ok(data) = serde_json::to_string_pretty(&settings_clone) {
        match std::fs::write(&path, data) {
            Ok(_) => println!("Settings saved successfully."),
            Err(e) => println!("Failed to save settings: {}", e),
        }
    }
}