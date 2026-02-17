import { useState } from "react";
import { MessageCircle, PanelLeftOpen, PanelLeftClose } from "lucide-react";
import { useChatStore } from "@/stores/chatStore";
import { ChatSidebar } from "@/components/chat/ChatSidebar";
import { MessageList } from "@/components/chat/MessageList";
import { ChatInput } from "@/components/chat/ChatInput";
import { useMediaQuery } from "@/hooks/useMediaQuery";
import { cn } from "@/lib/utils";

export function ChatPage() {
  const { activeSessionId, error, clearError, createSession } = useChatStore();
  const isDesktop = useMediaQuery("(min-width: 768px)");
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const handleNewChat = async () => {
    try {
      await createSession();
      setSidebarOpen(false);
    } catch {
      // Error handled in store
    }
  };

  return (
    <div className="flex h-full flex-col overflow-hidden">
      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar - always visible on desktop */}
        {isDesktop && <ChatSidebar />}

        {/* Mobile sidebar overlay */}
        {!isDesktop && sidebarOpen && (
          <>
            <div
              className="fixed inset-0 z-[var(--z-overlay,40)] bg-black/50"
              onClick={() => setSidebarOpen(false)}
            />
            <div className="fixed left-0 top-0 bottom-0 z-[var(--z-modal,50)] animate-fade-in">
              <ChatSidebar />
            </div>
          </>
        )}

        {/* Main chat area */}
        <div className="flex flex-1 flex-col overflow-hidden">
          {/* Chat header */}
          <div className="flex items-center gap-2 border-b border-[hsl(var(--border))] px-4 py-3">
            {!isDesktop && (
              <button
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className="rounded-lg p-1.5 text-[hsl(var(--muted-foreground))] hover:bg-[hsl(var(--muted))] hover:text-[hsl(var(--foreground))]"
                aria-label="Toggle sidebar"
              >
                {sidebarOpen ? (
                  <PanelLeftClose className="h-5 w-5" />
                ) : (
                  <PanelLeftOpen className="h-5 w-5" />
                )}
              </button>
            )}
            <h1 className="font-heading text-lg font-bold text-[hsl(var(--foreground))]">
              Chat
            </h1>
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

          {/* Messages or welcome state */}
          {activeSessionId ? (
            <>
              <MessageList />
              <ChatInput />
            </>
          ) : (
            <div className="flex flex-1 flex-col items-center justify-center px-4">
              <div className="flex flex-col items-center gap-4 text-center">
                <div
                  className={cn(
                    "flex h-16 w-16 items-center justify-center rounded-2xl",
                    "bg-[hsl(var(--primary))] text-[hsl(var(--primary-foreground))]",
                  )}
                >
                  <MessageCircle className="h-8 w-8" />
                </div>
                <div>
                  <h2 className="font-heading text-2xl font-bold text-[hsl(var(--foreground))]">
                    Toledot AI Chat
                  </h2>
                  <p className="mt-2 max-w-md text-sm text-[hsl(var(--muted-foreground))]">
                    Start a conversation about church history. Ask questions
                    about any era, figure, or event and get detailed answers
                    with source citations.
                  </p>
                </div>
                <button
                  onClick={handleNewChat}
                  className={cn(
                    "mt-2 rounded-lg px-6 py-2.5 text-sm font-medium",
                    "bg-[hsl(var(--primary))] text-[hsl(var(--primary-foreground))]",
                    "transition-colors hover:opacity-90",
                    "focus:outline-none focus:ring-2 focus:ring-[hsl(var(--ring))] focus:ring-offset-2",
                  )}
                >
                  Start a conversation
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
