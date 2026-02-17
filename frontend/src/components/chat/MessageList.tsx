import { useEffect, useRef } from "react";
import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Loader2 } from "lucide-react";
import { useChatStore } from "@/stores/chatStore";
import { MessageBubble } from "./MessageBubble";

export function MessageList() {
  const { messages, isStreaming, streamingContent, isLoadingMessages } =
    useChatStore();
  const bottomRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom on new messages or streaming content
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, streamingContent]);

  if (isLoadingMessages) {
    return (
      <div className="flex flex-1 items-center justify-center">
        <Loader2 className="h-6 w-6 animate-spin text-[hsl(var(--muted-foreground))]" />
        <span className="ml-2 text-sm text-[hsl(var(--muted-foreground))]">
          Loading messages...
        </span>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto px-4 py-6">
      <div className="mx-auto flex max-w-3xl flex-col gap-4">
        {messages.map((message) => (
          <MessageBubble key={message.id} message={message} />
        ))}

        {/* Streaming assistant message */}
        {isStreaming && (
          <div className="flex w-full justify-start">
            <div className="max-w-[80%] rounded-2xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] px-4 py-3 text-[hsl(var(--card-foreground))]">
              {streamingContent ? (
                <div className="prose prose-sm max-w-none dark:prose-invert">
                  <Markdown remarkPlugins={[remarkGfm]}>
                    {streamingContent}
                  </Markdown>
                </div>
              ) : (
                <div className="flex items-center gap-1.5">
                  <span className="text-sm text-[hsl(var(--muted-foreground))]">
                    Thinking
                  </span>
                  <span className="flex gap-0.5">
                    <span className="inline-block h-1.5 w-1.5 animate-bounce rounded-full bg-[hsl(var(--muted-foreground))]" style={{ animationDelay: "0ms" }} />
                    <span className="inline-block h-1.5 w-1.5 animate-bounce rounded-full bg-[hsl(var(--muted-foreground))]" style={{ animationDelay: "150ms" }} />
                    <span className="inline-block h-1.5 w-1.5 animate-bounce rounded-full bg-[hsl(var(--muted-foreground))]" style={{ animationDelay: "300ms" }} />
                  </span>
                </div>
              )}
              {/* Pulsing cursor */}
              {streamingContent && (
                <span className="ml-0.5 inline-block h-4 w-0.5 animate-pulse bg-[hsl(var(--foreground))]" />
              )}
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>
    </div>
  );
}
