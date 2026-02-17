import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { ExternalLink } from "lucide-react";
import type { ChatMessage } from "@/types";
import { cn } from "@/lib/utils";

type MessageBubbleProps = {
  message: ChatMessage;
};

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "user";

  return (
    <div
      className={cn(
        "flex w-full",
        isUser ? "justify-end" : "justify-start",
      )}
    >
      <div
        className={cn(
          "max-w-[80%] rounded-2xl px-4 py-3",
          isUser
            ? "bg-[hsl(var(--primary))] text-[hsl(var(--primary-foreground))]"
            : "bg-[hsl(var(--card))] text-[hsl(var(--card-foreground))] border border-[hsl(var(--border))]",
        )}
      >
        {isUser ? (
          <p className="whitespace-pre-wrap text-sm leading-relaxed">
            {message.content}
          </p>
        ) : (
          <div className="prose prose-sm max-w-none dark:prose-invert">
            <Markdown
              remarkPlugins={[remarkGfm]}
              components={{
                p: ({ children }) => (
                  <p className="mb-2 last:mb-0 text-sm leading-relaxed text-[hsl(var(--card-foreground))]">
                    {children}
                  </p>
                ),
                ul: ({ children }) => (
                  <ul className="mb-2 list-disc pl-4 text-sm text-[hsl(var(--card-foreground))]">
                    {children}
                  </ul>
                ),
                ol: ({ children }) => (
                  <ol className="mb-2 list-decimal pl-4 text-sm text-[hsl(var(--card-foreground))]">
                    {children}
                  </ol>
                ),
                li: ({ children }) => (
                  <li className="mb-1 text-[hsl(var(--card-foreground))]">
                    {children}
                  </li>
                ),
                h1: ({ children }) => (
                  <h1 className="mb-2 mt-3 text-lg font-bold text-[hsl(var(--card-foreground))]">
                    {children}
                  </h1>
                ),
                h2: ({ children }) => (
                  <h2 className="mb-2 mt-3 text-base font-bold text-[hsl(var(--card-foreground))]">
                    {children}
                  </h2>
                ),
                h3: ({ children }) => (
                  <h3 className="mb-1 mt-2 text-sm font-bold text-[hsl(var(--card-foreground))]">
                    {children}
                  </h3>
                ),
                code: ({ children, className }) => {
                  const isInline = !className;
                  return isInline ? (
                    <code className="rounded bg-[hsl(var(--muted))] px-1.5 py-0.5 text-xs font-mono text-[hsl(var(--foreground))]">
                      {children}
                    </code>
                  ) : (
                    <code className="text-xs font-mono">{children}</code>
                  );
                },
                pre: ({ children }) => (
                  <pre className="mb-2 overflow-x-auto rounded-lg bg-[hsl(var(--muted))] p-3 text-xs">
                    {children}
                  </pre>
                ),
                blockquote: ({ children }) => (
                  <blockquote className="mb-2 border-l-2 border-[hsl(var(--border))] pl-3 italic text-[hsl(var(--muted-foreground))]">
                    {children}
                  </blockquote>
                ),
                a: ({ href, children }) => (
                  <a
                    href={href}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-[hsl(var(--primary))] underline hover:no-underline"
                  >
                    {children}
                  </a>
                ),
              }}
            >
              {message.content}
            </Markdown>
          </div>
        )}

        {/* Source Citations */}
        {!isUser && message.sources && message.sources.length > 0 && (
          <div className="mt-3 flex flex-wrap gap-1.5 border-t border-[hsl(var(--border))] pt-2">
            {message.sources.map((source, index) => (
              <a
                key={index}
                href={source.url}
                target="_blank"
                rel="noopener noreferrer"
                className={cn(
                  "inline-flex items-center gap-1 rounded-full px-2.5 py-1",
                  "bg-[hsl(var(--muted))] text-xs text-[hsl(var(--muted-foreground))]",
                  "transition-colors hover:bg-[hsl(var(--secondary))] hover:text-[hsl(var(--foreground))]",
                )}
                title={source.source}
              >
                <ExternalLink className="h-3 w-3" />
                {source.title}
              </a>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
