import { useState, useEffect, useCallback } from "react";
import { Sidebar } from "./components/layout/Sidebar";
import { ResearchForm } from "./components/research/ResearchForm";
import { ProgressPanel } from "./components/research/ProgressPanel";
import { LogPanel } from "./components/research/LogPanel";
import { ReportViewer } from "./components/research/ReportViewer";
import { SettingsPanel } from "./components/settings/SettingsPanel";
import { HistoryList } from "./components/history/HistoryList";
import { useResearch } from "./hooks/useResearch";
import { useTheme } from "./hooks/useTheme";
import { useSettings } from "./stores/settings";
import { useHistory } from "./stores/useHistory";
import { validateSettings } from "./lib/api";
import { ArrowLeft, Search, RotateCcw } from "lucide-react";
import { Button } from "./components/ui/button";

const DEFAULTS = { depth: 3, maxPages: 25, numRounds: 2, timeLimit: 30 };

function App() {
  const [activeTab, setActiveTab] = useState<"research" | "settings" | "history">("research");
  const [viewingHistoryReport, setViewingHistoryReport] = useState<{ content: string; path: string } | null>(null);
  const { state, start, cancel, reset, loadReport } = useResearch();
  const { settings, loaded, load, setResearchDepth, setMaxPages, setNumRounds, setTimeLimit, save } = useSettings();
  const { loadReports } = useHistory();
  useTheme();

  useEffect(() => { load(); }, [load]);

  useEffect(() => {
    if (state.reportPath && !state.reportContent) {
      loadReport(state.reportPath);
    }
  }, [state.reportPath, state.reportContent, loadReport]);

  const handleViewHistoryReport = (report: { path: string; title: string }) => {
    loadReport(report.path).then((content) => {
      setViewingHistoryReport({ content, path: report.path });
      setActiveTab("research");
    });
  };

  const handleBackToHistory = () => {
    setViewingHistoryReport(null);
    setActiveTab("history");
    loadReports();
  };

  const handleStart = useCallback(async (topic: string) => {
    if (!settings) return;
    await save();
    await start(topic, settings);
  }, [settings, save, start]);

  const isViewingPastReport = !!viewingHistoryReport;
  const depth = settings?.researchDepth ?? DEFAULTS.depth;
  const maxPages = settings?.maxPagesPerQuery ?? DEFAULTS.maxPages;
  const numRounds = settings?.numRounds ?? DEFAULTS.numRounds;
  const timeLimit = settings?.timeLimitMinutes ?? DEFAULTS.timeLimit;
  const validation = settings ? validateSettings(settings) : { valid: true };

  if (!loaded) {
    return (
      <div className="h-screen w-screen flex items-center justify-center bg-background">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 rounded-full border-2 border-primary/30 border-t-primary animate-spin" />
          <p className="text-sm text-muted-foreground">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen w-screen flex overflow-hidden bg-background">
      <Sidebar activeTab={activeTab} onTabChange={setActiveTab} />

      <main className="flex-1 flex flex-col min-w-0">
        {activeTab === "research" && (
          <div className="flex-1 flex flex-col min-h-0">
            <header className="shrink-0 px-6 py-3 border-b border-border bg-surface-elevated">
              <div className="flex items-center gap-2 mb-3">
                <Search className="w-4 h-4 text-muted-foreground" />
                <h1 className="text-sm font-semibold">Research</h1>
                {(state.status === "done" || state.status === "error" || state.status === "cancelled") && !isViewingPastReport && (
                  <Button variant="outline" size="sm" onClick={reset} className="h-7 gap-1 text-xs ml-auto px-2.5">
                    <RotateCcw className="w-3 h-3" />
                    New
                  </Button>
                )}
              </div>
              {!isViewingPastReport && (
                <ResearchForm
                  onStart={handleStart}
                  onCancel={cancel}
                  isRunning={state.status === "running"}
                  depth={depth}
                  maxPages={maxPages}
                  numRounds={numRounds}
                  onDepthChange={setResearchDepth}
                  onPagesChange={setMaxPages}
                  onRoundsChange={setNumRounds}
                  timeLimit={timeLimit}
                  onTimeLimitChange={setTimeLimit}
                  validationError={!validation.valid ? validation.message : undefined}
                />
              )}
              {isViewingPastReport && (
                <Button variant="ghost" size="sm" onClick={handleBackToHistory} className="gap-1.5 -ml-2">
                  <ArrowLeft className="w-3.5 h-3.5" />
                  Back to History
                </Button>
              )}
            </header>

            <div className="flex-1 flex flex-col gap-3 p-5 min-h-0 overflow-auto">
              {state.status === "idle" && !isViewingPastReport && (
                <div className="flex-1 flex items-center justify-center">
                  <div className="text-center max-w-sm">
                    <Search className="w-8 h-8 text-muted-foreground/30 mx-auto mb-3" />
                    <h3 className="text-sm font-medium mb-1">Ready to research</h3>
                    <p className="text-xs text-muted-foreground leading-relaxed">
                      Enter a topic above. The agent will search the web, extract facts,
                      and produce a cited markdown report.
                    </p>
                  </div>
                </div>
              )}

              {state.status !== "idle" && !isViewingPastReport && (
                <>
                  <ProgressPanel state={state} />
                  <LogPanel logs={state.logs} />
                  {(state.status === "error" || state.status === "cancelled") && (
                    <div className="rounded-md border border-destructive/20 bg-destructive/5 px-3 py-2.5">
                      <p className="text-xs font-medium text-destructive">
                        {state.status === "cancelled" ? "Cancelled" : "Error"}
                      </p>
                      {state.errorMessage && (
                        <p className="text-xs text-muted-foreground mt-0.5">{state.errorMessage}</p>
                      )}
                    </div>
                  )}
                  {state.reportContent && (
                    <ReportViewer content={state.reportContent} path={state.reportPath} />
                  )}
                </>
              )}

              {isViewingPastReport && (
                <ReportViewer
                  content={viewingHistoryReport.content}
                  path={viewingHistoryReport.path}
                />
              )}
            </div>
          </div>
        )}

        {activeTab === "settings" && <SettingsPanel />}
        {activeTab === "history" && (
          <HistoryList onViewReport={handleViewHistoryReport} />
        )}
      </main>
    </div>
  );
}

export default App;
