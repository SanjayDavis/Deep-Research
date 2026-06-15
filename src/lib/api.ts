import { invoke } from "@tauri-apps/api/core";
import { AppSettings, ResearchSession, ReportMeta } from "./types";

export async function startResearch(topic: string, settings: AppSettings): Promise<void> {
  return invoke("start_research", { topic, settings });
}

export async function cancelResearch(): Promise<void> {
  return invoke("cancel_research");
}

export async function getSettings(): Promise<AppSettings> {
  return invoke("get_settings");
}

export async function saveSettings(settings: AppSettings): Promise<void> {
  return invoke("save_settings", { settings });
}

export async function fetchModels(baseUrl: string, apiKey: string): Promise<string[]> {
  return invoke("fetch_models", { baseUrl, apiKey });
}

export async function getResearchSession(): Promise<ResearchSession> {
  return invoke("get_research_state");
}

export async function getReportContent(path: string): Promise<string> {
  return invoke("get_report_content", { path });
}

export async function listReports(): Promise<ReportMeta[]> {
  return invoke("list_reports");
}

export async function deleteReport(path: string): Promise<void> {
  return invoke("delete_report", { path });
}

export async function searchReports(query: string): Promise<ReportMeta[]> {
  return invoke("search_reports", { query });
}

export async function openReportsFolder(): Promise<void> {
  return invoke("open_reports_folder");
}

export function validateSettings(settings: AppSettings): { valid: boolean; message?: string } {
  const provider = settings.providers[settings.provider];
  if (!provider?.model?.trim()) {
    return { valid: false, message: "Select a model in Settings before starting research." };
  }
  if (settings.provider === "openrouter" && (!provider.apiKey || provider.apiKey.length < 8)) {
    return { valid: false, message: "OpenRouter requires a valid API key in Settings." };
  }
  return { valid: true };
}
