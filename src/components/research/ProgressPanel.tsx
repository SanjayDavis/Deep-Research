import { ResearchProgress } from "../../lib/types";
import { StageNode } from "./StageNode";
import { ScrollArea } from "../ui/scroll-area";

function formatElapsed(seconds?: number): string {
  if (seconds == null) return "";
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  if (m > 0) return `${m}m ${s}s`;
  return `${s}s`;
}

interface ProgressPanelProps {
  state: ResearchProgress;
}

export function ProgressPanel({ state }: ProgressPanelProps) {
  if (state.status === "idle") return null;

  const doneCount = state.stages.filter((s) => s.status === "done").length;
  const progress = state.stages.length > 0 ? Math.round((doneCount / state.stages.length) * 100) : 0;

  return (
    <div className="panel">
      <div className="panel-header">
        <div className="flex items-center gap-2">
          <span className="section-title">Progress</span>
          <span className="text-[10px] text-muted-foreground">
            {state.status === "running" && `${doneCount}/${state.stages.length} stages`}
            {state.status === "done" && "Complete"}
            {state.status === "error" && "Failed"}
            {state.status === "cancelled" && "Cancelled"}
          </span>
        </div>
        <div className="flex items-center gap-2 text-xs">
          {state.round != null && state.roundTotal != null && state.status === "running" && (
            <span className="text-[10px] text-muted-foreground bg-muted px-1.5 py-0.5 rounded">
              Round {state.round}/{state.roundTotal}
            </span>
          )}
          {state.elapsed != null && state.status === "running" && (
            <span className="font-mono text-[10px] text-muted-foreground bg-muted px-1.5 py-0.5 rounded">
              {formatElapsed(state.elapsed)}
            </span>
          )}
          {state.status === "done" && (
            <span className="text-[10px] text-stage-done bg-stage-done/10 px-1.5 py-0.5 rounded">
              Done
            </span>
          )}
        </div>
      </div>
      {state.status === "running" && (
        <div className="px-4 pt-3">
          <div className="h-1 rounded-full bg-secondary overflow-hidden">
            <div
              className="h-full rounded-full bg-primary transition-all duration-500"
              style={{ width: `${progress}%` }}
            />
          </div>
          <p className="text-[10px] text-muted-foreground mt-0.5 text-right">{progress}%</p>
        </div>
      )}
      <ScrollArea className="max-h-[260px]">
        <div className="px-4 py-3">
          {state.stages.map((stage, i) => (
            <StageNode
              key={stage.id}
              stage={stage}
              isLast={i === state.stages.length - 1}
            />
          ))}
        </div>
      </ScrollArea>
    </div>
  );
}
