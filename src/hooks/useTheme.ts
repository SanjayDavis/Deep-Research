import { useEffect } from "react";
import { useSettings } from "../stores/settings";

export function useTheme() {
  const { settings, loaded, setTheme } = useSettings();

  useEffect(() => {
    if (!loaded || !settings) return;
    const root = document.documentElement;
    root.classList.remove("light", "dark");
    root.classList.add(settings.theme);
  }, [loaded, settings?.theme]);

  return {
    theme: settings?.theme ?? "dark",
    setTheme,
    loaded,
  };
}
