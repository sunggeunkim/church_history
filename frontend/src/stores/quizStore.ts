import { create } from "zustand";
import type { Quiz, QuizFeedback, QuizHistoryItem, QuizStats } from "@/types";
import {
  createQuiz,
  fetchQuiz,
  fetchQuizHistory,
  submitAnswer,
  completeQuiz,
  fetchQuizStats,
} from "@/services/quizApi";

type QuizState = {
  // Active quiz
  activeQuiz: Quiz | null;
  currentQuestionIndex: number;
  currentFeedback: QuizFeedback | null;

  // Quiz history
  quizHistory: QuizHistoryItem[];
  quizStats: QuizStats | null;

  // Loading states
  isCreatingQuiz: boolean;
  isSubmittingAnswer: boolean;
  isLoadingHistory: boolean;
  error: string | null;

  // Actions
  startQuiz: (eraId: number | null, difficulty: string, questionCount: number) => Promise<void>;
  submitQuizAnswer: (questionId: number, answer: string) => Promise<void>;
  nextQuestion: () => void;
  finishQuiz: () => Promise<void>;
  loadQuizHistory: () => Promise<void>;
  loadQuizStats: () => Promise<void>;
  viewQuiz: (quizId: number) => Promise<void>;
  resetActiveQuiz: () => void;
  clearError: () => void;
};

export const useQuizStore = create<QuizState>((set, get) => ({
  activeQuiz: null,
  currentQuestionIndex: 0,
  currentFeedback: null,
  quizHistory: [],
  quizStats: null,
  isCreatingQuiz: false,
  isSubmittingAnswer: false,
  isLoadingHistory: false,
  error: null,

  startQuiz: async (eraId, difficulty, questionCount) => {
    try {
      set({ isCreatingQuiz: true, error: null });
      const quiz = await createQuiz(eraId, difficulty, questionCount);
      set({
        activeQuiz: quiz,
        currentQuestionIndex: 0,
        currentFeedback: null,
        isCreatingQuiz: false,
      });
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : "Failed to create quiz",
        isCreatingQuiz: false,
      });
    }
  },

  submitQuizAnswer: async (questionId, answer) => {
    try {
      set({ isSubmittingAnswer: true, error: null });
      const feedback = await submitAnswer(
        get().activeQuiz!.id,
        questionId,
        answer
      );
      set({
        currentFeedback: feedback,
        isSubmittingAnswer: false,
      });
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : "Failed to submit answer",
        isSubmittingAnswer: false,
      });
    }
  },

  nextQuestion: () => {
    const { activeQuiz, currentQuestionIndex } = get();
    if (!activeQuiz) return;

    if (currentQuestionIndex < activeQuiz.questions.length - 1) {
      set({
        currentQuestionIndex: currentQuestionIndex + 1,
        currentFeedback: null,
      });
    } else {
      // Last question - trigger completion
      get().finishQuiz();
    }
  },

  finishQuiz: async () => {
    const { activeQuiz } = get();
    if (!activeQuiz) return;

    try {
      const result = await completeQuiz(activeQuiz.id);
      set((state) => ({
        activeQuiz: state.activeQuiz
          ? { ...state.activeQuiz, ...result }
          : null,
      }));
      // Reload history to include this quiz
      get().loadQuizHistory();
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : "Failed to complete quiz",
      });
    }
  },

  loadQuizHistory: async () => {
    try {
      set({ isLoadingHistory: true, error: null });
      const history = await fetchQuizHistory();
      set({ quizHistory: history, isLoadingHistory: false });
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : "Failed to load quiz history",
        isLoadingHistory: false,
      });
    }
  },

  loadQuizStats: async () => {
    try {
      const stats = await fetchQuizStats();
      set({ quizStats: stats });
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : "Failed to load quiz stats",
      });
    }
  },

  viewQuiz: async (quizId) => {
    try {
      const quiz = await fetchQuiz(quizId);
      set({
        activeQuiz: quiz,
        currentQuestionIndex: 0,
        currentFeedback: null,
      });
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : "Failed to load quiz",
      });
    }
  },

  resetActiveQuiz: () => {
    set({
      activeQuiz: null,
      currentQuestionIndex: 0,
      currentFeedback: null,
    });
  },

  clearError: () => {
    set({ error: null });
  },
}));
