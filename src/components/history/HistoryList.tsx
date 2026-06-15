import { useEffect } from "react";
import { History, Loader2 } from "lucide-react";
import { useHistory } from "../../stores/useHistory";
import { HistorySearch } from "./HistorySearch";
import { ReportCard } from "./ReportCard";
import { ScrollArea } from "../ui/scroll-area";
import { ReportMeta } from "../../lib/types";

interface HistoryListProps {
  onViewReport: (report: ReportMeta) => void;
}

export function HistoryList({ onViewReport }: HistoryListProps) {
  const { reports, filteredReports, loading, loadReports, searchQuery } = useHistory();

  useEffect(() => {
    loadReports();
  }, [loadReports]);

  return (
    <div className="flex-1 flex flex-col min-h-0">
      <header className="shrink-0 px-6 py-4 border-b border-border/40">
        <h1 className="text-base font-semibold tracking-tight">History</h1>
        <p className="text-xs text-muted-foreground mt-0.5">
          {reports.length} report{reports.length !== 1 ? "s" : ""} saved locally
        </p>
        <div className="mt-3 max-w-sm">
          <HistorySearch />
        </div>
      </header>

      {loading && reports.length === 0 ? (
        <div className="flex-1 flex items-center justify-center">
          <Loader2 className="w-5 h-5 text-primary animate-spin" />
        </div>
      ) : filteredReports.length === 0 ? (
        <div className="flex-1 flex items-center justify-center">
           <div className="text-center max-w-xs">
            <History className="w-10 h-10 text-muted-foreground/30 mx-auto mb-3" />
            <p className="text-sm text-muted-foreground">
              {searchQuery ? `No reports matching "${searchQuery}"` : "No research history yet"}
            </p>
            <p className="text-xs text-muted-foreground/60 mt-1">
              {searchQuery ? "Try a different search term" : "Completed reports appear here"}
            </p>
          </div>
        </div>
      ) : (
        <ScrollArea className="flex-1 min-h-0">
          <div className="p-5 space-y-2">
            {filteredReports.map((report) => (
              <ReportCard key={report.path} report={report} onView={onViewReport} />
            ))}
          </div>
        </ScrollArea>
      )}
    </div>
  );
}
