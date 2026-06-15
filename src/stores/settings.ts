import { create } from "zustand";
import { AppSettings, ProviderType } from "../lib/types";
import * as api from "../lib/api";

interface SettingsStore {
  settings: AppSettings | null;
  loaded: boolean;
  load: () => Promise<void>;
  setProvider: (type: ProviderType) => void;
  setBaseUrl: (type: ProviderType, url: string) => void;
  setModel: (type: ProviderType, model: string) => void;
  setModels: (type: ProviderType, models: string[]) => void;
  setApiKey: (type: ProviderType, key: string) => void;
  setSearxngUrl: (url: string) => void;
  setResearchDepth: (depth: number) => void;
  setMaxPages: (pages: number) => void;
  setNumRounds: (rounds: number) => void;
  setTimeLimit: (minutes: number) => void;
  setTheme: (theme: "dark" | "light") => void;
  save: () => Promise<void>;
}

export const useSettings = create<SettingsStore>((set, get) => ({
  settings: null,
  loaded: false,

  load: async () => {
    try {
      const s = await api.getSettings();
      set({ settings: s, loaded: true });
    } catch {
      set({ settings: null, loaded: true });
    }
  },

  setProvider: (type) => {
    set((s) => {
      if (!s.settings) return s;
      return { settings: { ...s.settings, provider: type } };
    });
  },

  setBaseUrl: (type, url) => {
    set((s) => {
      if (!s.settings) return s;
      return {
        settings: {
          ...s.settings,
          providers: {
            ...s.settings.providers,
            [type]: { ...s.settings.providers[type], baseUrl: url },
          },
        },
      };
    });
  },

  setModel: (type, model) => {
    set((s) => {
      if (!s.settings) return s;
      return {
        settings: {
          ...s.settings,
          providers: {
            ...s.settings.providers,
            [type]: { ...s.settings.providers[type], model },
          },
        },
      };
    });
  },

  setModels: (type, models) => {
    set((s) => {
      if (!s.settings) return s;
      return {
        settings: {
          ...s.settings,
          providers: {
            ...s.settings.providers,
            [type]: { ...s.settings.providers[type], models },
          },
        },
      };
    });
  },

  setApiKey: (type, key) => {
    set((s) => {
      if (!s.settings) return s;
      return {
        settings: {
          ...s.settings,
          providers: {
            ...s.settings.providers,
            [type]: { ...s.settings.providers[type], apiKey: key },
          },
        },
      };
    });
  },

  setSearxngUrl: (url) => {
    set((s) => {
      if (!s.settings) return s;
      return { settings: { ...s.settings, searxngUrl: url } };
    });
  },

  setResearchDepth: (depth) => {
    set((s) => {
      if (!s.settings) return s;
      return { settings: { ...s.settings, researchDepth: depth } };
    });
  },

  setMaxPages: (pages) => {
    set((s) => {
      if (!s.settings) return s;
      return { settings: { ...s.settings, maxPagesPerQuery: pages } };
    });
  },

  setNumRounds: (rounds) => {
    set((s) => {
      if (!s.settings) return s;
      return { settings: { ...s.settings, numRounds: rounds } };
    });
  },

  setTimeLimit: (minutes) => {
    set((s) => {
      if (!s.settings) return s;
      return { settings: { ...s.settings, timeLimitMinutes: minutes } };
    });
  },

  setTheme: (theme) => {
    set((s) => {
      if (!s.settings) return s;
      return { settings: { ...s.settings, theme } };
    });
  },

  save: async () => {
    const { settings } = get();
    if (settings) {
      await api.saveSettings(settings);
    }
  },
}));
