import { create } from "zustand";
import type { Era } from "@/types";
import { fetchEras, fetchEra } from "@/services/api";

type EraState = {
  eras: Era[];
  selectedEra: Era | null;
  isLoading: boolean;
  error: string | null;
  fetchEras: () => Promise<void>;
  fetchEra: (slug: string) => Promise<void>;
  selectEra: (era: Era | null) => void;
};

export const useEraStore = create<EraState>((set) => ({
  eras: [],
  selectedEra: null,
  isLoading: false,
  error: null,

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
}));
