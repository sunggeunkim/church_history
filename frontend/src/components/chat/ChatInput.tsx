import { useState, useRef, useCallback } from "react";
import { Send, Square } from "lucide-react";
import { useChatStore } from "@/stores/chatStore";
import { cn } from "@/lib/utils";

export function ChatInput() {
  const [input, setInput] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const { sendMessage, isStreaming, cancelStream, activeSessionId } =
    useChatStore();

  const handleSend = useCallback(async () => {
    const trimmed = input.trim();
    if (!trimmed || isStreaming || !activeSessionId) return;

    setInput("");
    // Reset textarea height
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }

    await sendMessage(trimmed);
  }, [input, isStreaming, activeSessionId, sendMessage]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleInput = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value);
    // Auto-resize textarea
    const textarea = e.target;
    textarea.style.height = "auto";
    textarea.style.height = `${Math.min(textarea.scrollHeight, 200)}px`;
  };

  const canSend = input.trim().length > 0 && !isStreaming && !!activeSessionId;

  return (
    <div className="border-t border-[hsl(var(--border))] bg-[hsl(var(--background))] px-4 py-3">
      <div className="mx-auto flex max-w-3xl items-end gap-2">
        <div className="relative flex-1">
          <textarea
            ref={textareaRef}
            value={input}
            onChange={handleInput}
            onKeyDown={handleKeyDown}
            placeholder={
              activeSessionId
                ? "Ask about church history..."
                : "Select or start a chat session"
            }
            disabled={!activeSessionId}
            rows={1}
            className={cn(
              "w-full resize-none rounded-xl border border-[hsl(var(--input))] bg-[hsl(var(--card))]",
              "px-4 py-3 pr-12 text-sm text-[hsl(var(--foreground))]",
              "placeholder:text-[hsl(var(--muted-foreground))]",
              "focus:border-[hsl(var(--ring))] focus:outline-none focus:ring-1 focus:ring-[hsl(var(--ring))]",
              "disabled:cursor-not-allowed disabled:opacity-50",
              "scrollbar-thin",
            )}
            aria-label="Chat message input"
          />
        </div>

        {isStreaming ? (
          <button
            onClick={cancelStream}
            className={cn(
              "flex h-10 w-10 shrink-0 items-center justify-center rounded-xl",
              "bg-[hsl(var(--destructive))] text-[hsl(var(--destructive-foreground))]",
              "transition-colors hover:opacity-90",
              "focus:outline-none focus:ring-2 focus:ring-[hsl(var(--ring))] focus:ring-offset-2",
            )}
            aria-label="Stop generating"
          >
            <Square className="h-4 w-4" />
          </button>
        ) : (
          <button
            onClick={handleSend}
            disabled={!canSend}
            className={cn(
              "flex h-10 w-10 shrink-0 items-center justify-center rounded-xl",
              "bg-[hsl(var(--primary))] text-[hsl(var(--primary-foreground))]",
              "transition-colors hover:opacity-90",
              "focus:outline-none focus:ring-2 focus:ring-[hsl(var(--ring))] focus:ring-offset-2",
              "disabled:cursor-not-allowed disabled:opacity-50",
            )}
            aria-label="Send message"
          >
            <Send className="h-4 w-4" />
          </button>
        )}
      </div>
    </div>
  );
}
