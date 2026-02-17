import { fetchEventSource } from "@microsoft/fetch-event-source";
import api from "./api";
import type { ChatSession, ChatMessage, SourceCitation } from "@/types";

// Map snake_case session response to camelCase ChatSession
function mapSession(data: Record<string, unknown>): ChatSession {
  return {
    id: String(data.id),
    title: data.title as string,
    eraId: data.era != null ? String(data.era) : null,
    createdAt: data.created_at as string,
    updatedAt: data.updated_at as string,
  };
}

// Map snake_case message response to camelCase ChatMessage
function mapMessage(data: Record<string, unknown>): ChatMessage {
  const citations = data.citations as Record<string, unknown>[] | undefined;
  return {
    id: String(data.id),
    role: data.role as "user" | "assistant",
    content: data.content as string,
    createdAt: data.created_at as string,
    sources: citations?.map(mapCitation),
  };
}

// Map citation response to SourceCitation
function mapCitation(data: Record<string, unknown>): SourceCitation {
  return {
    title: data.title as string,
    url: (data.url as string) || "",
    source: (data.source_name as string) || (data.source as string) || "",
  };
}

export async function fetchSessions(): Promise<ChatSession[]> {
  const response = await api.get("/chat/sessions/");
  return response.data.results.map(mapSession);
}

export async function createChatSession(
  eraId?: string | null,
): Promise<ChatSession> {
  const response = await api.post("/chat/sessions/", {
    era: eraId || null,
  });
  return mapSession(response.data);
}

export async function deleteChatSession(sessionId: string): Promise<void> {
  await api.delete(`/chat/sessions/${sessionId}/`);
}

export async function fetchMessages(
  sessionId: string,
): Promise<ChatMessage[]> {
  const response = await api.get(`/chat/sessions/${sessionId}/messages/`);
  // Messages endpoint has pagination disabled - returns a plain array
  return response.data.map(mapMessage);
}

// SSE streaming function - returns abort controller
export function streamChatMessage(
  sessionId: string,
  message: string,
  csrfToken: string,
  callbacks: {
    onDelta: (content: string) => void;
    onDone: (messageId: string, citations: SourceCitation[]) => void;
    onError: (error: Error) => void;
  },
): AbortController {
  const controller = new AbortController();
  const baseUrl = import.meta.env.VITE_API_BASE_URL || "/api";

  fetchEventSource(`${baseUrl}/chat/stream/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrfToken,
    },
    credentials: "include" as RequestCredentials,
    body: JSON.stringify({ session_id: sessionId, message }),
    signal: controller.signal,
    onmessage(event) {
      try {
        const data = JSON.parse(event.data);
        if (data.type === "delta") {
          callbacks.onDelta(data.content);
        }
        if (data.type === "done") {
          const citations: SourceCitation[] = (data.citations || []).map(
            (c: Record<string, unknown>) => mapCitation(c),
          );
          callbacks.onDone(data.message_id, citations);
        }
      } catch {
        // Ignore malformed events
      }
    },
    onerror(err) {
      callbacks.onError(
        err instanceof Error ? err : new Error("Stream failed"),
      );
      throw err; // Stop retrying
    },
  });

  return controller;
}
