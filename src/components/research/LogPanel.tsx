import { useRef, useEffect } from "react";
import { ScrollArea } from "../ui/scroll-area";
import { Terminal } from "lucide-react";

interface LogPanelProps {
  logs: string[];
  className?: string;
}

function getLogStyle(line: string) {
  if (line.includes("[ERROR]") || line.includes("Error") || line.includes("error")) {
    return "text-stage-error/80";
  }
  if (line.includes("[DONE]") || line.includes("Complete")) {
    return "text-stage-done/80";
  }
  if (line.includes("[SEARCH]")) {
    return "text-blue-400/80";
  }
  if (line.includes("[SCRAPING]") || line.includes("[SCRAPE]")) {
    return "text-amber-400/80";
  }
  if (line.includes("[EXTRACT]")) {
    return "text-purple-400/80";
  }
  if (line.includes("[SYNTHESISE]")) {
    return "text-cyan-400/80";
  }
  if (line.includes("[DECOMPOSE]")) {
    return "text-emerald-400/80";
  }
  if (line.includes("[TIME]")) {
    return "text-orange-400/80";
  }
  if (line.includes("[CHROMA]") || line.includes("[CHUNKING")) {
    return "text-violet-400/80";
  }
  if (line.includes("[CLEANUP]") || line.includes("[STORAGE]")) {
    return "text-teal-400/80";
  }
  return "text-muted-foreground";
}

export function LogPanel({ logs, className }: LogPanelProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logs.length]);

  if (logs.length === 0) return null;

  return (
    <div className={`panel ${className ?? ""}`}>
      <div className="panel-header py-2">
        <div className="flex items-center gap-1.5">
          <Terminal className="w-3.5 h-3.5 text-muted-foreground" />
          <span className="section-title">Log</span>
        </div>
        <span className="text-[10px] text-muted-foreground bg-muted px-1.5 py-0.5 rounded">{logs.length} lines</span>
      </div>
      <ScrollArea className="max-h-[160px]">
        <div className="px-3 py-2 font-mono text-[11px] leading-relaxed space-y-0.5">
          {logs.map((line, i) => (
            <div key={i} className={`${getLogStyle(line)} truncate`} title={line}>
              <span className="text-muted-foreground/20 mr-1.5 select-none">{String(i + 1).padStart(3, "0")}</span>
              {line}
            </div>
          ))}
          <div ref={bottomRef} />
        </div>
      </ScrollArea>
    </div>
  );
}
