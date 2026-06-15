import { cn } from "../../lib/utils";
import { Button } from "../ui/button";
import {
  Search,
  Settings2,
  History,
  Moon,
  Sun,
  PanelRightOpen,
} from "lucide-react";
import { useTheme } from "../../hooks/useTheme";
import { useSettings } from "../../stores/settings";

interface SidebarProps {
  activeTab: "research" | "settings" | "history";
  onTabChange: (tab: "research" | "settings" | "history") => void;
}

const navItems = [
  { id: "research" as const, label: "Research", icon: Search },
  { id: "history" as const, label: "History", icon: History },
  { id: "settings" as const, label: "Settings", icon: Settings2 },
];

export function Sidebar({ activeTab, onTabChange }: SidebarProps) {
  const { theme, setTheme } = useTheme();
  const { save } = useSettings();

  const toggleTheme = async () => {
    setTheme(theme === "dark" ? "light" : "dark");
    setTimeout(() => save(), 0);
  };

  return (
    <aside className="w-56 bg-sidebar border-r border-sidebar-border flex flex-col h-full shrink-0">
      <div className="flex items-center gap-2.5 px-4 h-12 border-b border-sidebar-border">
        <PanelRightOpen className="w-4 h-4 text-sidebar-muted" />
        <span className="text-sm font-semibold text-sidebar-foreground">
          Deep Research
        </span>
      </div>

      <nav className="flex-1 px-2 py-3 space-y-0.5">
        {navItems.map((item) => {
          const active = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onTabChange(item.id)}
              className={cn(
                "flex items-center gap-2.5 w-full px-3 py-2 rounded-md text-left transition-all duration-150",
                active
                  ? "bg-accent text-foreground"
                  : "text-sidebar-muted hover:text-sidebar-foreground hover:bg-accent/50"
              )}
            >
              <item.icon className="w-4 h-4" />
              <span className="text-sm">{item.label}</span>
            </button>
          );
        })}
      </nav>

      <div className="px-2 py-2 border-t border-sidebar-border">
        <Button
          variant="ghost"
          size="sm"
          onClick={toggleTheme}
          className="w-full justify-start gap-2 h-8 text-xs text-sidebar-muted hover:text-sidebar-foreground rounded-md"
        >
          {theme === "dark" ? <Sun className="w-3.5 h-3.5" /> : <Moon className="w-3.5 h-3.5" />}
          {theme === "dark" ? "Light mode" : "Dark mode"}
        </Button>
      </div>
    </aside>
  );
}
