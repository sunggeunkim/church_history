import { create } from "zustand";
import type { Era } from "@/types";
import { fetchEras, fetchEra, fetchTimeline } from "@/services/api";

type EraState = {
  eras: Era[];
  selectedEra: Era | null;
  isLoading: boolean;
  error: string | null;
  // Canvas state
  timelineData: Era[] | null;
  expandedEraId: number | null;
  isLoadingTimeline: boolean;

  fetchEras: () => Promise<void>;
  fetchEra: (slug: string) => Promise<void>;
  selectEra: (era: Era | null) => void;
  fetchTimeline: () => Promise<void>;
  toggleExpanded: (eraId: number) => void;
  setExpandedEra: (eraId: number | null) => void;
};

export const useEraStore = create<EraState>((set, get) => ({
  eras: [],
  selectedEra: null,
  isLoading: false,
  error: null,
  timelineData: null,
  expandedEraId: null,
  isLoadingTimeline: false,

  fetchEras: async () => {
    try {
      set({ isLoading: true, error: null });
      const eras = await fetchEras();
      set({ eras, isLoading: false });
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : "Failed to fetch eras",
        isLoading: false,
      });
    }
  },

  fetchEra: async (slug: string) => {
    try {
      set({ isLoading: true, error: null });
      const era = await fetchEra(slug);
      set({ selectedEra: era, isLoading: false });
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : "Failed to fetch era",
        isLoading: false,
      });
    }
  },

  selectEra: (era: Era | null) => {
    set({ selectedEra: era });
  },

  fetchTimeline: async () => {
    if (get().timelineData) return; // Already cached
    try {
      set({ isLoadingTimeline: true, error: null });
      const data = await fetchTimeline();
      set({ timelineData: data, isLoadingTimeline: false });
    } catch (error) {
      set({
        error:
          error instanceof Error ? error.message : "Failed to fetch timeline",
        isLoadingTimeline: false,
      });
    }
  },

  toggleExpanded: (eraId: number) => {
    set((state) => ({
      expandedEraId: state.expandedEraId === eraId ? null : eraId,
    }));
  },

  setExpandedEra: (eraId: number | null) => {
    set({ expandedEraId: eraId });
  },
}));
