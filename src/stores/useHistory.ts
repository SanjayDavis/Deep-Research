import { create } from "zustand";
import { ReportMeta } from "../lib/types";
import * as api from "../lib/api";

interface HistoryStore {
  reports: ReportMeta[];
  filteredReports: ReportMeta[];
  loading: boolean;
  searchQuery: string;
  loadReports: () => Promise<void>;
  search: (query: string) => Promise<void>;
  clearSearch: () => void;
  deleteReport: (path: string) => Promise<void>;
}

export const useHistory = create<HistoryStore>((set, get) => ({
  reports: [],
  filteredReports: [],
  loading: false,
  searchQuery: "",

  loadReports: async () => {
    set({ loading: true });
    try {
      const reports = await api.listReports();
      set({ reports, filteredReports: reports, loading: false });
    } catch {
      set({ reports: [], filteredReports: [], loading: false });
    }
  },

  search: async (query: string) => {
    set({ searchQuery: query, loading: true });
    if (!query.trim()) {
      set({ filteredReports: get().reports, loading: false });
      return;
    }
    try {
      const reports = await api.searchReports(query);
      set({ filteredReports: reports, loading: false });
    } catch {
      set({ filteredReports: [], loading: false });
    }
  },

  clearSearch: () => {
    set({ searchQuery: "", filteredReports: get().reports });
  },

  deleteReport: async (path: string) => {
    await api.deleteReport(path);
    set((state) => ({
      reports: state.reports.filter((r) => r.path !== path),
      filteredReports: state.filteredReports.filter((r) => r.path !== path),
    }));
  },
}));