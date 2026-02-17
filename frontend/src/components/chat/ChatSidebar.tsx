import { useEffect } from "react";
import { Plus, Trash2, MessageCircle, Loader2 } from "lucide-react";
import { useChatStore } from "@/stores/chatStore";
import { cn } from "@/lib/utils";

export function ChatSidebar() {
  const {
    sessions,
    activeSessionId,
    isLoadingSessions,
    loadSessions,
    createSession,
    deleteSession,
    setActiveSession,
  } = useChatStore();

  useEffect(() => {
    loadSessions();
  }, [loadSessions]);

  const handleNewChat = async () => {
    try {
      await createSession();
    } catch {
      // Error is handled in the store
    }
  };

  const handleDelete = async (
    e: React.MouseEvent,
    sessionId: string,
  ) => {
    e.stopPropagation();
    await deleteSession(sessionId);
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffDays === 0) return "Today";
    if (diffDays === 1) return "Yesterday";
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString(undefined, {
      month: "short",
      day: "numeric",
    });
  };

  return (
    <div className="flex h-full w-64 flex-col border-r border-[hsl(var(--border))] bg-[hsl(var(--card))]">
      {/* New Chat Button */}
      <div className="p-3">
        <button
          onClick={handleNewChat}
          className={cn(
            "flex w-full items-center justify-center gap-2 rounded-lg px-4 py-2.5",
            "bg-[hsl(var(--primary))] text-[hsl(var(--primary-foreground))]",
            "text-sm font-medium transition-colors",
            "hover:opacity-90 focus:outline-none focus:ring-2 focus:ring-[hsl(var(--ring))] focus:ring-offset-2",
          )}
        >
          <Plus className="h-4 w-4" />
          New Chat
        </button>
      </div>

      {/* Sessions List */}
      <div className="flex-1 overflow-y-auto px-2 pb-2">
        {isLoadingSessions ? (
          <div className="flex items-center justify-center py-8">
            <Loader2 className="h-5 w-5 animate-spin text-[hsl(var(--muted-foreground))]" />
          </div>
        ) : sessions.length === 0 ? (
          <p className="px-3 py-8 text-center text-sm text-[hsl(var(--muted-foreground))]">
            No conversations yet
          </p>
        ) : (
          <ul className="flex flex-col gap-1" role="list">
            {sessions.map((session) => (
              <li key={session.id}>
                <div
                  role="button"
                  tabIndex={0}
                  onClick={() => setActiveSession(session.id)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" || e.key === " ") {
                      e.preventDefault();
                      setActiveSession(session.id);
                    }
                  }}
                  className={cn(
                    "group flex w-full cursor-pointer items-start gap-2 rounded-lg px-3 py-2.5 text-left text-sm transition-colors",
                    activeSessionId === session.id
                      ? "bg-[hsl(var(--muted))] text-[hsl(var(--foreground))]"
                      : "text-[hsl(var(--muted-foreground))] hover:bg-[hsl(var(--muted))] hover:text-[hsl(var(--foreground))]",
                  )}
                  aria-current={
                    activeSessionId === session.id ? "true" : undefined
                  }
                >
                  <MessageCircle className="mt-0.5 h-4 w-4 shrink-0" />
                  <div className="min-w-0 flex-1">
                    <p className="truncate font-medium">{session.title}</p>
                    <p className="text-xs text-[hsl(var(--muted-foreground))]">
                      {formatDate(session.updatedAt)}
                    </p>
                  </div>
                  <button
                    onClick={(e) => handleDelete(e, session.id)}
                    className={cn(
                      "shrink-0 rounded p-1 opacity-0 transition-opacity",
                      "hover:bg-[hsl(var(--destructive))] hover:text-[hsl(var(--destructive-foreground))]",
                      "group-hover:opacity-100 focus:opacity-100 focus:outline-none",
                    )}
                    aria-label={`Delete ${session.title}`}
                  >
                    <Trash2 className="h-3.5 w-3.5" />
                  </button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
