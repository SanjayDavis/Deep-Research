import { Search, X } from "lucide-react";
import { useHistory } from "../../stores/useHistory";
import { Input } from "../ui/input";

export function HistorySearch() {
  const { searchQuery, search, clearSearch } = useHistory();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    search(e.target.value);
  };

  const handleClear = () => {
    clearSearch();
  };

  return (
    <div className="relative">
      <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground/60" />
      <Input
        placeholder="Search history..."
        value={searchQuery}
        onChange={handleChange}
        className="pl-9 pr-9"
      />
      {searchQuery && (
        <button
          onClick={handleClear}
          className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground/60 hover:text-muted-foreground"
          aria-label="Clear search"
        >
          <X className="w-4 h-4" />
        </button>
      )}
    </div>
  );
}