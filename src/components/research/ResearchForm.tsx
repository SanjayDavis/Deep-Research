import { useState, useRef, useEffect } from "react";
import { Button } from "../ui/button";
import { Search, Square, Zap, Scale, Telescope } from "lucide-react";
import { cn } from "../../lib/utils";

type Preset = "quick" | "balanced" | "deep";

interface PresetConfig {
  label: string;
  icon: typeof Zap;
  depth: number;
  pages: number;
  rounds: number;
  timeLimit: number;
  desc: string;
}

const PRESETS: Record<Preset, PresetConfig> = {
  quick: { label: "Quick", icon: Zap, depth: 1, pages: 10, rounds: 1, timeLimit: 10, desc: "~10 min" },
  balanced: { label: "Balanced", icon: Scale, depth: 3, pages: 25, rounds: 2, timeLimit: 30, desc: "~30 min" },
  deep: { label: "Deep", icon: Telescope, depth: 5, pages: 50, rounds: 3, timeLimit: 60, desc: "~60 min" },
};

interface ResearchFormProps {
  onStart: (topic: string) => void;
  onCancel: () => void;
  isRunning: boolean;
  depth: number;
  maxPages: number;
  numRounds: number;
  timeLimit: number;
  onDepthChange: (d: number) => void;
  onPagesChange: (p: number) => void;
  onRoundsChange: (r: number) => void;
  onTimeLimitChange: (t: number) => void;
  validationError?: string;
}

const SUGGESTIONS = [
  "Latest breakthroughs in quantum computing",
  "Comparison of AI agent frameworks",
  "Impact of Rust on systems programming",
  "Solid-state battery technology advances",
];

function ParamControl({
  label,
  value,
  min,
  max,
  onChange,
}: {
  label: string;
  value: number;
  min: number;
  max: number;
  onChange: (v: number) => void;
}) {
  return (
    <div className="flex items-center gap-2">
      <span className="text-[11px] text-muted-foreground w-12 shrink-0">{label}</span>
      <input
        type="number"
        min={min}
        max={max}
        value={value}
        onChange={(e) => onChange(Math.min(max, Math.max(min, Number(e.target.value))))}
        className="w-14 h-7 rounded border border-input bg-background px-2 text-xs tabular-nums text-center focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
      />
    </div>
  );
}

export function ResearchForm({
  onStart,
  onCancel,
  isRunning,
  depth,
  maxPages,
  numRounds,
  timeLimit,
  onDepthChange,
  onPagesChange,
  onRoundsChange,
  onTimeLimitChange,
  validationError,
}: ResearchFormProps) {
  const [topic, setTopic] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (!isRunning) inputRef.current?.focus();
  }, [isRunning]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (topic.trim() && !isRunning) onStart(topic.trim());
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      <div className="flex gap-2">
        <div className="relative flex-1">
          <input
            ref={inputRef}
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            placeholder="Enter a research topic..."
            disabled={isRunning}
            className="input-field disabled:opacity-60"
          />
        </div>
        {isRunning ? (
          <Button
            type="button"
            variant="outline"
            onClick={onCancel}
            className="h-9 px-4 gap-1.5 text-destructive border-destructive/40 hover:bg-destructive/10 hover:text-destructive shrink-0"
          >
            <Square className="w-3.5 h-3.5 fill-current" />
            Stop
          </Button>
        ) : (
          <Button
            type="submit"
            disabled={!topic.trim()}
            className="h-9 px-5 gap-1.5 shrink-0"
          >
            <Search className="w-3.5 h-3.5" />
            Research
          </Button>
        )}
      </div>

      {validationError && !isRunning && (
        <div className="flex items-start gap-2 px-3 py-2 rounded-md bg-destructive/10 border border-destructive/20 text-xs text-destructive">
          <span>{validationError}</span>
        </div>
      )}

      {!isRunning && (
        <div className="flex flex-wrap items-center gap-2">
          <div className="flex flex-wrap gap-1.5 flex-1">
            {SUGGESTIONS.map((s) => (
              <button
                key={s}
                type="button"
                onClick={() => setTopic(s)}
                className="text-[11px] px-2 py-1 rounded-md bg-secondary text-muted-foreground hover:text-foreground hover:bg-accent transition-colors"
              >
                {s}
              </button>
            ))}
          </div>
          <div className="flex items-center gap-1">
            {(Object.entries(PRESETS) as [Preset, PresetConfig][]).map(([key, p]) => {
              const Icon = p.icon;
              const active = depth === p.depth && maxPages === p.pages && numRounds === p.rounds && timeLimit === p.timeLimit;
              return (
                <button
                  key={key}
                  type="button"
                  onClick={() => { onDepthChange(p.depth); onPagesChange(p.pages); onRoundsChange(p.rounds); onTimeLimitChange(p.timeLimit); }}
                  className={cn(
                    "flex items-center gap-1 text-[11px] px-2 py-1 rounded-md border transition-colors",
                    active
                      ? "bg-primary/10 text-primary border-primary/30"
                      : "bg-secondary text-muted-foreground hover:text-foreground hover:bg-accent border-transparent"
                  )}
                  title={p.desc}
                >
                  <Icon className="w-3 h-3" />
                  {p.label}
                </button>
              );
            })}
          </div>
        </div>
      )}

      {!isRunning && (
        <div className="flex flex-wrap items-center gap-x-4 gap-y-1.5 px-3 py-2 rounded-md border border-border bg-surface-overlay">
          <ParamControl label="Depth" value={depth} min={1} max={15} onChange={onDepthChange} />
          <ParamControl label="Pages" value={maxPages} min={1} max={50} onChange={onPagesChange} />
          <ParamControl label="Rounds" value={numRounds} min={1} max={10} onChange={onRoundsChange} />
          <ParamControl label="Time(min)" value={timeLimit} min={5} max={120} onChange={onTimeLimitChange} />
        </div>
      )}
    </form>
  );
}
