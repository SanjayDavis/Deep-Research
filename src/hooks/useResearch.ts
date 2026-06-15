import { useState, useCallback, useRef, useEffect } from "react";
import { listen, UnlistenFn } from "@tauri-apps/api/event";
import { ProgressEvent, ResearchStage, ResearchProgress, AppSettings } from "../lib/types";
import * as api from "../lib/api";

const STAGE_DEFS: { id: string; label: string; description: string }[] = [
  { id: "decompose", label: "Decompose", description: "Breaking down the research topic" },
  { id: "search", label: "Search", description: "Querying the web" },
  { id: "scrape", label: "Scrape", description: "Extracting page content" },
  { id: "chunk", label: "Index", description: "Chunking and embedding text" },
  { id: "extract", label: "Extract", description: "Pulling key facts via RAG" },
  { id: "synthesise", label: "Synthesise", description: "Writing the final report" },
];

const MAX_LOGS = 500;

function emptyStages(): ResearchStage[] {
  return STAGE_DEFS.map((d) => ({
    ...d,
    status: "pending" as const,
    progress: 0,
    message: "",
  }));
}

export function useResearch() {
  const [state, setState] = useState<ResearchProgress>({
    topic: "",
    stages: emptyStages(),
    status: "idle",
    logs: [],
  });
  const unlistenRef = useRef<UnlistenFn | null>(null);

  useEffect(() => {
    (async () => {
      try {
        unlistenRef.current = await listen<ProgressEvent>("research-event", (event) => {
          const e = event.payload;
          setState((prev) => {
            if (e.type === "log") {
              const logs = [...prev.logs, e.message].slice(-MAX_LOGS);
              return { ...prev, logs };
            }
            if (e.type === "progress" && e.stage) {
              const stageIdx = prev.stages.findIndex((s) => s.id === e.stage);
              if (stageIdx === -1) return prev;
              const stages = [...prev.stages];
              stages[stageIdx] = {
                ...stages[stageIdx],
                status: "active",
                message: e.message,
                progress: e.pct ?? stages[stageIdx].progress,
                elapsed: e.elapsed ?? stages[stageIdx].elapsed,
              };
              for (let i = 0; i < stageIdx; i++) {
                if (stages[i].status === "pending") {
                  stages[i] = { ...stages[i], status: "done", progress: 100 };
                }
              }
              const logs = [...prev.logs, e.message].slice(-MAX_LOGS);
              return {
                ...prev,
                stages,
                status: "running",
                round: e.round ?? prev.round,
                roundTotal: e.roundTotal ?? prev.roundTotal,
                elapsed: e.elapsed ?? prev.elapsed,
                logs,
              };
            }
            if (e.type === "result") {
              const result = e.data as { path?: string; content?: string };
              const stages = prev.stages.map((s) =>
                s.status === "active" || s.status === "pending"
                  ? { ...s, status: "done" as const, progress: 100 }
                  : s
              );
              return {
                ...prev,
                stages,
                status: "done",
                reportPath: result?.path,
                reportContent: result?.content,
              };
            }
            if (e.type === "error") {
              const stages = prev.stages.map((s) =>
                s.status === "active" ? { ...s, status: "error" as const, message: e.message } : s
              );
              return { ...prev, stages, status: "error", errorMessage: e.message };
            }
            if (e.type === "cancelled") {
              return { ...prev, status: "cancelled", errorMessage: e.message };
            }
            return prev;
          });
        });

        const session = await api.getResearchSession();
        if (session.running) {
          setState((prev) => ({
            ...prev,
            topic: session.topic,
            status: "running",
            errorMessage: "A previous research session was interrupted.",
          }));
        }
      } catch {
        console.warn("[Deep Research] Event listener unavailable (browser mode)");
      }
    })();
    return () => { unlistenRef.current?.(); };
  }, []);

  const start = useCallback(async (topic: string, settings: AppSettings) => {
    const validation = api.validateSettings(settings);
    if (!validation.valid) {
      setState((prev) => ({ ...prev, status: "error", errorMessage: validation.message }));
      throw new Error(validation.message);
    }
    setState({ topic, stages: emptyStages(), status: "running", logs: [] });
    try {
      await api.startResearch(topic, settings);
    } catch (err) {
      setState((prev) => ({ ...prev, status: "error", errorMessage: String(err) }));
      throw err;
    }
  }, []);

  const cancel = useCallback(async () => {
    try { await api.cancelResearch(); } catch { /* ignore */ }
    setState((prev) => ({ ...prev, status: "cancelled" }));
  }, []);

  const reset = useCallback(() => {
    setState({ topic: "", stages: emptyStages(), status: "idle", logs: [] });
  }, []);

  const loadReport = useCallback(async (path: string): Promise<string> => {
    try {
      const content = await api.getReportContent(path);
      setState((prev) => ({ ...prev, reportContent: content, reportPath: path }));
      return content;
    } catch {
      return "";
    }
  }, []);

  return { state, start, cancel, reset, loadReport };
}
