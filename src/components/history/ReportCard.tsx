import { FileText, Trash2, ChevronRight } from "lucide-react";
import { ReportMeta } from "../../lib/types";
import { useHistory } from "../../stores/useHistory";
import { Button } from "../ui/button";
import { format } from "date-fns";

interface ReportCardProps {
  report: ReportMeta;
  onView: (report: ReportMeta) => void;
}

export function ReportCard({ report, onView }: ReportCardProps) {
  const { deleteReport } = useHistory();

  const formatDate = (dateStr: string) => {
    try {
      return format(new Date(dateStr), "MMM d, yyyy · HH:mm");
    } catch {
      return dateStr;
    }
  };

  const handleDelete = async (e: React.MouseEvent) => {
    e.stopPropagation();
    if (confirm(`Delete "${report.title}"?`)) {
      await deleteReport(report.path);
    }
  };

  return (
    <div
      className="group card-modern flex items-center gap-3 px-4 py-3"
      onClick={() => onView(report)}
    >
      <div className="w-8 h-8 rounded-md bg-primary/10 flex items-center justify-center shrink-0">
        <FileText className="w-3.5 h-3.5 text-primary" />
      </div>
      <div className="flex-1 min-w-0">
        <h4 className="text-sm font-medium truncate">{report.title}</h4>
        <div className="flex items-center gap-2 mt-0.5">
          <span className="text-[11px] text-muted-foreground">{formatDate(report.date)}</span>
          <span className="text-[10px] text-muted-foreground/30">·</span>
          <span className="text-[11px] text-muted-foreground">{report.wordCount.toLocaleString()} words</span>
          <span className="text-[10px] text-muted-foreground/30">·</span>
          <span className="text-[11px] text-muted-foreground">{report.sourceCount} sources</span>
        </div>
      </div>
      <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity shrink-0">
        <Button
          variant="ghost"
          size="icon"
          className="h-7 w-7 text-destructive/70 hover:text-destructive hover:bg-destructive/10 rounded"
          onClick={handleDelete}
          aria-label="Delete report"
        >
          <Trash2 className="w-3.5 h-3.5" />
        </Button>
        <ChevronRight className="w-3.5 h-3.5 text-muted-foreground/40" />
      </div>
    </div>
  );
}
