import { useState, useRef, useEffect, useMemo } from "react";
import { cn } from "../../lib/utils";
import { ChevronDown, Search } from "lucide-react";

interface Option {
  value: string;
  label: string;
  searchTerms?: string[];
}

interface SearchableSelectProps {
  options: Option[];
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  className?: string;
  emptyMessage?: string;
}

export function SearchableSelect({
  options,
  value,
  onChange,
  placeholder = "Select...",
  className,
  emptyMessage = "No options found",
}: SearchableSelectProps) {
  const [open, setOpen] = useState(false);
  const [search, setSearch] = useState("");
  const containerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const listRef = useRef<HTMLDivElement>(null);
  const [highlightIdx, setHighlightIdx] = useState(0);

  const filtered = useMemo(() => {
    if (!search.trim()) return options;
    const q = search.toLowerCase();
    const terms = q.split(/\s+/).filter(Boolean);
    return options.filter((o) => {
      const haystack = [o.label.toLowerCase(), o.value.toLowerCase(), ...(o.searchTerms ?? [])].join(" ");
      return terms.every((t) => haystack.includes(t));
    });
  }, [options, search]);

  const selectedLabel = options.find((o) => o.value === value)?.label ?? "";

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  useEffect(() => {
    if (open) {
      inputRef.current?.focus();
      setHighlightIdx(0);
    }
  }, [open]);

  useEffect(() => {
    setHighlightIdx(0);
  }, [search]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setHighlightIdx((i) => Math.min(i + 1, filtered.length - 1));
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setHighlightIdx((i) => Math.max(i - 1, 0));
    } else if (e.key === "Enter" && filtered[highlightIdx]) {
      e.preventDefault();
      onChange(filtered[highlightIdx].value);
      setOpen(false);
      setSearch("");
    } else if (e.key === "Escape") {
      setOpen(false);
      setSearch("");
    }
  };

  return (
    <div ref={containerRef} className={cn("relative", className)}>
      <button
        type="button"
        onClick={() => setOpen(!open)}
        className={cn(
          "flex items-center gap-2 w-full h-9 rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm",
          "hover:bg-accent/50 transition-colors",
          !value && "text-muted-foreground"
        )}
      >
        <Search className="w-3.5 h-3.5 text-muted-foreground shrink-0" />
        <span className="flex-1 text-left truncate">
          {selectedLabel || placeholder}
        </span>
        <span className="text-[11px] text-muted-foreground shrink-0">
          {options.length}
        </span>
        <ChevronDown className={cn("w-3.5 h-3.5 text-muted-foreground transition-transform", open && "rotate-180")} />
      </button>

      {open && (
        <div
          className="fixed z-50 mt-1 rounded-lg border border-border bg-popover shadow-lg overflow-hidden"
          style={{
            top: containerRef.current ? containerRef.current.getBoundingClientRect().bottom + 4 : 0,
            left: containerRef.current ? containerRef.current.getBoundingClientRect().left : 0,
            width: containerRef.current ? containerRef.current.getBoundingClientRect().width : 0,
          }}
        >
          <div className="p-1.5 border-b border-border/50">
            <input
              ref={inputRef}
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Type to filter..."
              className="w-full h-8 rounded-md bg-background px-2.5 text-xs outline-none placeholder:text-muted-foreground/50 border border-input/50 focus:border-primary/50"
            />
          </div>

          <div
            ref={listRef}
            className="max-h-60 overflow-y-auto"
            onKeyDown={handleKeyDown}
          >
            {filtered.length === 0 ? (
              <div className="px-3 py-6 text-center text-xs text-muted-foreground">
                {emptyMessage}
              </div>
            ) : (
              filtered.map((opt, idx) => (
                <button
                  key={opt.value}
                  type="button"
                  onClick={() => {
                    onChange(opt.value);
                    setOpen(false);
                    setSearch("");
                  }}
                  onMouseEnter={() => setHighlightIdx(idx)}
                  className={cn(
                    "flex items-center gap-2 w-full px-3 py-2 text-xs text-left transition-colors",
                    idx === highlightIdx && "bg-accent text-accent-foreground",
                    opt.value === value && "text-primary font-medium",
                    opt.value !== value && "text-popover-foreground"
                  )}
                >
                  <span className="flex-1 truncate">{opt.label}</span>
                  {opt.value === value && (
                    <span className="w-1.5 h-1.5 rounded-full bg-primary shrink-0" />
                  )}
                </button>
              ))
            )}
          </div>

          <div className="px-3 py-1.5 border-t border-border/50 text-[11px] text-muted-foreground flex items-center justify-between">
            <span>{filtered.length} / {options.length}</span>
            <span className="text-[10px]">↑↓ navigate ↵ select</span>
          </div>
        </div>
      )}
    </div>
  );
}