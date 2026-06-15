import { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeHighlight from "rehype-highlight";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import "katex/dist/katex.min.css";
import { ScrollArea } from "../ui/scroll-area";
import { Button } from "../ui/button";
import { prepareReportForPreview } from "../../lib/reportUtils";
import * as api from "../../lib/api";
import { FileText, Eye, Copy, Check, FolderOpen } from "lucide-react";

interface ReportViewerProps {
  content?: string;
  path?: string;
}

export function ReportViewer({ content, path }: ReportViewerProps) {
  const [view, setView] = useState<"rendered" | "raw">("rendered");
  const [copied, setCopied] = useState(false);

  if (!content) return null;

  const displayContent = view === "rendered" ? prepareReportForPreview(content) : content;

  const handleCopy = async () => {
    await navigator.clipboard.writeText(content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleOpenFolder = async () => {
    try {
      await api.openReportsFolder();
    } catch { /* ignore */ }
  };

  return (
    <div className="panel flex flex-col flex-1 min-h-0">
      <div className="panel-header">
        <div className="flex items-center gap-1">
          <Button
            variant={view === "rendered" ? "secondary" : "ghost"}
            size="sm"
            onClick={() => setView("rendered")}
            className="h-7 gap-1 text-xs px-2.5"
          >
            <Eye className="w-3 h-3" />
            Preview
          </Button>
          <Button
            variant={view === "raw" ? "secondary" : "ghost"}
            size="sm"
            onClick={() => setView("raw")}
            className="h-7 gap-1 text-xs px-2.5"
          >
            <FileText className="w-3 h-3" />
            Source
          </Button>
        </div>
        <div className="flex items-center gap-1">
          <Button variant="ghost" size="sm" onClick={handleCopy} className="h-7 gap-1 text-xs px-2.5">
            {copied ? <Check className="w-3 h-3 text-stage-done" /> : <Copy className="w-3 h-3" />}
            {copied ? "Copied" : "Copy"}
          </Button>
          <Button variant="ghost" size="sm" onClick={handleOpenFolder} className="h-7 gap-1 text-xs px-2.5">
            <FolderOpen className="w-3 h-3" />
            Folder
          </Button>
          {path && (
            <span className="text-[10px] text-muted-foreground font-mono ml-2 max-w-[140px] truncate hidden sm:block bg-muted px-1.5 py-0.5 rounded">
              {path.split("/").pop()}
            </span>
          )}
        </div>
      </div>
      <ScrollArea className="flex-1 min-h-0">
        {view === "rendered" ? (
          <div className="prose prose-sm dark:prose-invert max-w-none px-6 py-5
            prose-headings:font-semibold prose-headings:tracking-tight
            prose-a:text-primary prose-code:text-primary
            prose-pre:bg-muted prose-pre:border prose-pre:border-border prose-pre:rounded-md
            prose-table:border-collapse prose-th:bg-muted prose-td:border-border
            prose-blockquote:border-l-primary prose-blockquote:bg-muted/30 prose-blockquote:rounded-r-md
            [&>*:first-child]:mt-0 [&>*:last-child]:mb-0">
            <ReactMarkdown remarkPlugins={[remarkGfm, remarkMath] as any} rehypePlugins={[rehypeHighlight, rehypeKatex] as any}>
              {displayContent}
            </ReactMarkdown>
          </div>
        ) : (
          <pre className="px-6 py-5 text-[11px] font-mono text-foreground/75 leading-relaxed whitespace-pre-wrap bg-muted/20">
            {displayContent}
          </pre>
        )}
      </ScrollArea>
    </div>
  );
}
