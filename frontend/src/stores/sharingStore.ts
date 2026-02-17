import { create } from "zustand";
import { createShareLink as apiCreateShareLink } from "@/services/sharingApi";

type SharingState = {
  // Modal state
  isModalOpen: boolean;
  shareUrl: string | null;
  shareText: string;
  shareType: "achievement" | "quiz_result" | "progress" | null;

  // Loading
  isCreating: boolean;
  error: string | null;

  // Actions
  createShareLink: (
    shareType: "achievement" | "quiz_result" | "progress",
    achievementId?: number,
    quizId?: number,
  ) => Promise<void>;
  closeModal: () => void;
  clearError: () => void;
};

function buildShareText(
  shareType: string,
  snapshot: Record<string, unknown>,
): string {
  switch (shareType) {
    case "achievement":
      return `I just unlocked "${snapshot.achievement_name}" on Toledot!`;
    case "quiz_result":
      return `I scored ${snapshot.percentage_score}% on a ${snapshot.era_name} church history quiz on Toledot!`;
    case "progress":
      return `I'm ${snapshot.completion_percentage}% through my church history journey on Toledot!`;
    default:
      return "Check out what I'm learning on Toledot!";
  }
}

export const useSharingStore = create<SharingState>((set) => ({
  isModalOpen: false,
  shareUrl: null,
  shareText: "",
  shareType: null,
  isCreating: false,
  error: null,

  createShareLink: async (shareType, achievementId, quizId) => {
    try {
      set({ isCreating: true, error: null });
      const result = await apiCreateShareLink(shareType, achievementId, quizId);

      const shareText = buildShareText(shareType, result.content_snapshot);

      set({
        isModalOpen: true,
        shareUrl: result.share_url,
        shareText,
        shareType,
        isCreating: false,
      });
    } catch (error) {
      set({
        error:
          error instanceof Error
            ? error.message
            : "Failed to create share link",
        isCreating: false,
      });
    }
  },

  closeModal: () => {
    set({
      isModalOpen: false,
      shareUrl: null,
      shareText: "",
      shareType: null,
    });
  },

  clearError: () => {
    set({ error: null });
  },
}));
