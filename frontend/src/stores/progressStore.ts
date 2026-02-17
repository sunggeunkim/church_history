import { create } from "zustand";
import type { ProgressSummary, Achievement } from "@/types";
import {
  fetchProgressSummary,
  markEraVisited,
  fetchAchievements,
  checkAchievements,
} from "@/services/progressApi";

type ProgressState = {
  // Progress data
  summary: ProgressSummary | null;
  achievements: Achievement[];
  newlyUnlocked: Achievement[];

  // Loading states
  isLoading: boolean;
  isLoadingAchievements: boolean;
  error: string | null;

  // Actions
  loadSummary: () => Promise<void>;
  loadAchievements: () => Promise<void>;
  markEraVisited: (eraId: number) => Promise<void>;
  checkAchievements: () => Promise<void>;
  clearNewlyUnlocked: () => void;
  clearError: () => void;
};

export const useProgressStore = create<ProgressState>((set, get) => ({
  summary: null,
  achievements: [],
  newlyUnlocked: [],
  isLoading: false,
  isLoadingAchievements: false,
  error: null,

  loadSummary: async () => {
    try {
      set({ isLoading: true, error: null });
      const data = await fetchProgressSummary();
      set({
        summary: data,
        isLoading: false,
      });
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : "Failed to load progress",
        isLoading: false,
      });
    }
  },

  loadAchievements: async () => {
    try {
      set({ isLoadingAchievements: true, error: null });
      const data = await fetchAchievements();
      set({
        achievements: data.achievements,
        isLoadingAchievements: false,
      });
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : "Failed to load achievements",
        isLoadingAchievements: false,
      });
    }
  },

  markEraVisited: async (eraId: number) => {
    try {
      await markEraVisited(eraId);
      // Reload summary to get updated progress
      await get().loadSummary();
      // Check for newly unlocked achievements
      await get().checkAchievements();
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : "Failed to mark era as visited",
      });
    }
  },

  checkAchievements: async () => {
    try {
      const data = await checkAchievements();
      if (data.newlyUnlocked.length > 0) {
        set({
          newlyUnlocked: data.newlyUnlocked,
        });
        // Reload achievements to update unlock status
        await get().loadAchievements();
      }
    } catch (error) {
      console.error("Failed to check achievements:", error);
      // Don't set error state for this (non-critical)
    }
  },

  clearNewlyUnlocked: () => {
    set({ newlyUnlocked: [] });
  },

  clearError: () => {
    set({ error: null });
  },
}));
