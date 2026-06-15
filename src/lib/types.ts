export type ProviderType = "openrouter" | "lm-studio" | "opencode-proxy";

export interface ProviderConfig {
  type: ProviderType;
  label: string;
  baseUrl: string;
  apiKey: string;
  model: string;
  models?: string[];
}

export interface McpConfig {
  enabled: boolean;
  port: number;
}

export interface McpStatus {
  running: boolean;
  port: number;
}

export interface AppSettings {
  provider: ProviderType;
  providers: Record<ProviderType, ProviderConfig>;
  searxngUrl: string;
  theme: "dark" | "light";
  researchDepth: number;
  maxPagesPerQuery: number;
  numRounds: number;
  timeLimitMinutes: number;
  mcp: McpConfig;
}

export interface ProgressEvent {
  type: "progress" | "result" | "error" | "log" | "cancelled";
  stage?: string;
  message: string;
  pct?: number;
  subtask?: string;
  round?: number;
  roundTotal?: number;
  elapsed?: number;
  data?: unknown;
}

export interface ResearchStage {
  id: string;
  label: string;
  description: string;
  status: "pending" | "active" | "done" | "error";
  progress: number;
  message: string;
  elapsed?: number;
}

export interface ResearchProgress {
  topic: string;
  stages: ResearchStage[];
  status: "idle" | "running" | "done" | "error" | "cancelled";
  reportPath?: string;
  reportContent?: string;
  errorMessage?: string;
  round?: number;
  roundTotal?: number;
  elapsed?: number;
  logs: string[];
}

/** Rust-side session tracker (running + topic only) */
export interface ResearchSession {
  running: boolean;
  topic: string;
}

export interface ReportMeta {
  path: string;
  filename: string;
  title: string;
  date: string;
  wordCount: number;
  sourceCount: number;
  rounds: number;
  depth: number;
  sessionId: string;
}

export interface ValidationResult {
  valid: boolean;
  message?: string;
}
