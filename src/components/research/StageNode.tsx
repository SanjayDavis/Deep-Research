import { cn } from "../../lib/utils";
import { ResearchStage } from "../../lib/types";
import { Check, Loader2, X, Circle } from "lucide-react";

interface StageNodeProps {
  stage: ResearchStage;
  isLast: boolean;
}

export function StageNode({ stage, isLast }: StageNodeProps) {
  const icon = () => {
    switch (stage.status) {
      case "done":
        return (
          <div className="w-5 h-5 rounded-full bg-stage-done/15 flex items-center justify-center">
            <Check className="w-3 h-3 text-stage-done" />
          </div>
        );
      case "active":
        return (
          <div className="w-5 h-5 rounded-full bg-stage-active/15 flex items-center justify-center">
            <Loader2 className="w-3 h-3 text-stage-active animate-spin" />
          </div>
        );
      case "error":
        return (
          <div className="w-5 h-5 rounded-full bg-stage-error/15 flex items-center justify-center">
            <X className="w-3 h-3 text-stage-error" />
          </div>
        );
      default:
        return (
          <div className="w-5 h-5 rounded-full bg-muted flex items-center justify-center">
            <Circle className="w-2 h-2 text-muted-foreground/30 fill-current" />
          </div>
        );
    }
  };

  return (
    <div className="flex gap-2.5">
      <div className="flex flex-col items-center">
        {icon()}
        {!isLast && (
          <div className={cn(
            "w-px flex-1 min-h-[20px] mt-1",
            stage.status === "done" ? "bg-stage-done/30" : "bg-border"
          )} />
        )}
      </div>
      <div className={cn("flex-1 min-w-0", !isLast && "pb-3")}>
        <div className="flex items-center gap-2">
          <span
            className={cn(
              "text-xs font-medium",
              stage.status === "active" && "text-stage-active",
              stage.status === "done" && "text-foreground",
              stage.status === "error" && "text-stage-error",
              stage.status === "pending" && "text-muted-foreground/50"
            )}
          >
            {stage.label}
          </span>
          {stage.status === "active" && stage.progress > 0 && (
            <span className="text-[10px] text-muted-foreground tabular-nums ml-auto">
              {stage.progress}%
            </span>
          )}
        </div>
        {stage.message && (
          <p className="text-[11px] text-muted-foreground mt-0.5 truncate" title={stage.message}>
            {stage.message}
          </p>
        )}
        {stage.status === "active" && (
          <div className="mt-1.5 h-1 rounded-full bg-secondary overflow-hidden">
            <div
              className={cn(
                "h-full rounded-full transition-all duration-500",
                stage.progress > 0
                  ? "bg-stage-active"
                  : "bg-stage-active/30 w-1/3 animate-pulse"
              )}
              style={stage.progress > 0 ? { width: `${stage.progress}%` } : undefined}
            />
          </div>
        )}
      </div>
    </div>
  );
}
