import { create } from "zustand";
import type { ChatSession, ChatMessage, SourceCitation } from "@/types";
import {
  fetchSessions,
  createChatSession,
  deleteChatSession,
  fetchMessages,
  streamChatMessage,
} from "@/services/chatApi";
import api from "@/services/api";

type ChatState = {
  sessions: ChatSession[];
  activeSessionId: string | null;
  messages: ChatMessage[];
  isStreaming: boolean;
  streamingContent: string;
  isLoadingSessions: boolean;
  isLoadingMessages: boolean;
  error: string | null;

  // Actions
  loadSessions: () => Promise<void>;
  createSession: (eraId?: string | null) => Promise<ChatSession>;
  deleteSession: (sessionId: string) => Promise<void>;
  setActiveSession: (sessionId: string) => void;
  loadMessages: (sessionId: string) => Promise<void>;
  sendMessage: (content: string) => Promise<void>;
  cancelStream: () => void;
  clearError: () => void;
};

let abortController: AbortController | null = null;

export const useChatStore = create<ChatState>((set, get) => ({
  sessions: [],
  activeSessionId: null,
  messages: [],
  isStreaming: false,
  streamingContent: "",
  isLoadingSessions: false,
  isLoadingMessages: false,
  error: null,

  loadSessions: async () => {
    try {
      set({ isLoadingSessions: true, error: null });
      const sessions = await fetchSessions();
      set({ sessions, isLoadingSessions: false });
    } catch (error) {
      set({
        error:
          error instanceof Error
            ? error.message
            : "Failed to load chat sessions",
        isLoadingSessions: false,
      });
    }
  },

  createSession: async (eraId?: string | null) => {
    try {
      set({ error: null });
      const session = await createChatSession(eraId);
      set((state) => ({
        sessions: [session, ...state.sessions],
        activeSessionId: session.id,
        messages: [],
      }));
      return session;
    } catch (error) {
      const message =
        error instanceof Error
          ? error.message
          : "Failed to create chat session";
      set({ error: message });
      throw error;
    }
  },

  deleteSession: async (sessionId: string) => {
    try {
      set({ error: null });
      await deleteChatSession(sessionId);
      set((state) => {
        const sessions = state.sessions.filter((s) => s.id !== sessionId);
        const isActive = state.activeSessionId === sessionId;
        return {
          sessions,
          activeSessionId: isActive ? null : state.activeSessionId,
          messages: isActive ? [] : state.messages,
        };
      });
    } catch (error) {
      set({
        error:
          error instanceof Error
            ? error.message
            : "Failed to delete chat session",
      });
    }
  },

  setActiveSession: (sessionId: string) => {
    set({ activeSessionId: sessionId, messages: [], error: null });
    get().loadMessages(sessionId);
  },

  loadMessages: async (sessionId: string) => {
    try {
      set({ isLoadingMessages: true, error: null });
      const messages = await fetchMessages(sessionId);
      // Only update if this session is still the active one
      if (get().activeSessionId === sessionId) {
        set({ messages, isLoadingMessages: false });
      }
    } catch (error) {
      set({
        error:
          error instanceof Error ? error.message : "Failed to load messages",
        isLoadingMessages: false,
      });
    }
  },

  sendMessage: async (content: string) => {
    const { activeSessionId } = get();
    if (!activeSessionId) return;

    // Optimistically add user message
    const userMessage: ChatMessage = {
      id: `temp-${Date.now()}`,
      role: "user",
      content,
      createdAt: new Date().toISOString(),
    };

    set((state) => ({
      messages: [...state.messages, userMessage],
      isStreaming: true,
      streamingContent: "",
      error: null,
    }));

    // Get CSRF token from the axios instance defaults
    const csrfToken =
      (api.defaults.headers.common["X-CSRFToken"] as string) || "";

    abortController = streamChatMessage(
      activeSessionId,
      content,
      csrfToken,
      {
        onDelta: (delta: string) => {
          set((state) => ({
            streamingContent: state.streamingContent + delta,
          }));
        },
        onDone: (messageId: string, citations: SourceCitation[]) => {
          const assistantMessage: ChatMessage = {
            id: messageId,
            role: "assistant",
            content: get().streamingContent,
            createdAt: new Date().toISOString(),
            sources: citations.length > 0 ? citations : undefined,
          };
          set((state) => ({
            messages: [...state.messages, assistantMessage],
            isStreaming: false,
            streamingContent: "",
          }));
          abortController = null;

          // Reload sessions to pick up any title changes
          get().loadSessions();
        },
        onError: (error: Error) => {
          set({
            error: error.message || "Failed to get response",
            isStreaming: false,
            streamingContent: "",
          });
          abortController = null;
        },
      },
    );
  },

  cancelStream: () => {
    if (abortController) {
      abortController.abort();
      abortController = null;
    }
    set({ isStreaming: false, streamingContent: "" });
  },

  clearError: () => {
    set({ error: null });
  },
}));
