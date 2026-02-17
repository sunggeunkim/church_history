import { useEffect } from "react";
import { MessageSquare } from "lucide-react";
import type { Era } from "@/types";
import { useChatStore } from "@/stores/chatStore";
import { MessageList } from "@/components/chat/MessageList";
import { ChatInput } from "@/components/chat/ChatInput";
import { cn } from "@/lib/utils";

type CanvasChatPanelProps = {
  selectedEra: Era | null;
};

export function CanvasChatPanel({ selectedEra }: CanvasChatPanelProps) {
  const {
    activeSessionId,
    sessions,
    isLoadingSessions,
    error,
    clearError,
    loadSessions,
    createSession,
    setActiveSession,
  } = useChatStore();

  // Load sessions on mount
  useEffect(() => {
    if (sessions.length === 0 && !isLoadingSessions) {
      loadSessions();
    }
  }, [sessions.length, isLoadingSessions, loadSessions]);

  // When selected era changes, find or create a session for it
  useEffect(() => {
    if (!selectedEra || isLoadingSessions) return;

    const eraId = String(selectedEra.id);
    const existingSession = sessions.find((s) => s.eraId === eraId);

    if (existingSession) {
      if (activeSessionId !== existingSession.id) {
        setActiveSession(existingSession.id);
      }
    }
  }, [selectedEra, sessions, activeSessionId, setActiveSession, isLoadingSessions]);

  const handleStartChat = async () => {
    if (!selectedEra) return;
    try {
      await createSession(String(selectedEra.id));
    } catch {
      // Error handled in store
    }
  };

  // No era selected — show empty state
  if (!selectedEra) {
    return (
      <div className="flex h-full flex-col items-center justify-center px-6 text-center">
        <div
          className={cn(
            "flex h-14 w-14 items-center justify-center rounded-2xl",
            "bg-[hsl(var(--muted))] text-[hsl(var(--muted-foreground))]",
          )}
        >
          <MessageSquare className="h-7 w-7" />
        </div>
        <h3 className="mt-4 font-heading text-lg font-semibold text-[hsl(var(--foreground))]">
          Select an Era
        </h3>
        <p className="mt-2 max-w-xs text-sm text-[hsl(var(--muted-foreground))]">
          Click on an era in the timeline to start chatting about that period of
          church history.
        </p>
      </div>
    );
  }

  // Era selected but no active session
  if (!activeSessionId) {
    return (
      <div className="flex h-full flex-col">
        {/* Era header */}
        <div
          className="flex items-center gap-3 border-b px-4 py-3"
          style={{ borderBottomColor: selectedEra.color }}
        >
          <div
            className="h-3 w-3 rounded-full shrink-0"
            style={{ backgroundColor: selectedEra.color }}
          />
          <div className="min-w-0">
            <p className="text-sm font-semibold text-[hsl(var(--foreground))] truncate">
              {selectedEra.name}
            </p>
            <p className="text-xs text-[hsl(var(--muted-foreground))]">
              {selectedEra.startYear}–{selectedEra.endYear ?? "present"}
            </p>
          </div>
        </div>

        <div className="flex flex-1 flex-col items-center justify-center px-6 text-center">
          {error && (
            <div className="mb-4 w-full max-w-xs rounded-lg bg-[hsl(var(--destructive))] px-4 py-2 text-sm text-[hsl(var(--destructive-foreground))]">
              {error}
            </div>
          )}
          <p className="text-sm text-[hsl(var(--muted-foreground))] mb-4">
            Start a conversation about {selectedEra.name}
          </p>
          <button
            onClick={handleStartChat}
            className={cn(
              "flex items-center gap-2 rounded-lg px-5 py-2.5 text-sm font-medium",
              "text-white transition-colors hover:opacity-90",
              "focus:outline-none focus:ring-2 focus:ring-[hsl(var(--ring))] focus:ring-offset-2",
            )}
            style={{ backgroundColor: selectedEra.color }}
          >
            <MessageSquare className="h-4 w-4" />
            Start chatting
          </button>
        </div>
      </div>
    );
  }

  // Active session — show chat
  return (
    <div className="flex h-full flex-col">
      {/* Era context header */}
      <div
        className="flex items-center gap-3 border-b px-4 py-3"
        style={{ borderBottomColor: selectedEra.color }}
      >
        <div
          className="h-3 w-3 rounded-full shrink-0"
          style={{ backgroundColor: selectedEra.color }}
        />
        <div className="min-w-0">
          <p className="text-sm font-semibold text-[hsl(var(--foreground))] truncate">
            {selectedEra.name}
          </p>
          <p className="text-xs text-[hsl(var(--muted-foreground))]">
            {selectedEra.startYear}–{selectedEra.endYear ?? "present"}
          </p>
        </div>
      </div>

      {/* Error banner */}
      {error && (
        <div className="mx-4 mt-2 flex items-center justify-between rounded-lg bg-[hsl(var(--destructive))] px-4 py-2 text-sm text-[hsl(var(--destructive-foreground))]">
          <span>{error}</span>
          <button
            onClick={clearError}
            className="ml-2 font-medium underline hover:no-underline"
          >
            Dismiss
          </button>
        </div>
      )}

      <MessageList />
      <ChatInput />
    </div>
  );
}
