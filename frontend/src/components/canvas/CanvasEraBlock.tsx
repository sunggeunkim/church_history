import { useRef } from "react";
import { motion, AnimatePresence } from "motion/react";
import { ChevronDown, MessageSquare } from "lucide-react";
import type { Era } from "@/types";
import { cn } from "@/lib/utils";
import { CanvasEventList } from "./CanvasEventList";
import { CanvasFigureList } from "./CanvasFigureList";

type CanvasEraBlockProps = {
  era: Era;
  isExpanded: boolean;
  isSelected: boolean;
  onToggle: () => void;
  onChatClick: () => void;
};

export function CanvasEraBlock({
  era,
  isExpanded,
  isSelected,
  onToggle,
  onChatClick,
}: CanvasEraBlockProps) {
  const blockRef = useRef<HTMLDivElement>(null);

  return (
    <motion.div
      ref={blockRef}
      layout
      className={cn(
        "rounded-xl border-2 bg-[hsl(var(--card))] transition-shadow",
        isSelected && "ring-2 ring-[hsl(var(--ring))] ring-offset-2",
      )}
      style={{ borderTopColor: era.color, borderTopWidth: "4px" }}
    >
      {/* Header - always visible */}
      <button
        onClick={onToggle}
        className="flex w-full items-center justify-between p-4 text-left focus:outline-none"
        aria-expanded={isExpanded}
        aria-label={`${isExpanded ? "Collapse" : "Expand"} ${era.name}`}
      >
        <div className="flex-1 min-w-0">
          <h3 className="font-heading text-lg font-bold text-[hsl(var(--foreground))]">
            {era.name}
          </h3>
          <p className="text-sm" style={{ color: era.color }}>
            {era.startYear}–{era.endYear ?? "present"}
          </p>
          {!isExpanded && era.summary && (
            <p className="mt-1 text-sm text-[hsl(var(--muted-foreground))] line-clamp-2">
              {era.summary}
            </p>
          )}
        </div>
        <motion.div
          animate={{ rotate: isExpanded ? 180 : 0 }}
          transition={{ duration: 0.2 }}
          className="ml-2 shrink-0"
        >
          <ChevronDown className="h-5 w-5 text-[hsl(var(--muted-foreground))]" />
        </motion.div>
      </button>

      {/* Expanded content */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3, ease: "easeInOut" }}
            className="overflow-hidden"
          >
            <div className="px-4 pb-4 space-y-6">
              {/* Description */}
              <p className="text-sm text-[hsl(var(--foreground))] leading-relaxed">
                {era.description}
              </p>

              {/* Key Events */}
              {era.keyEvents && era.keyEvents.length > 0 && (
                <div>
                  <h4 className="text-sm font-semibold text-[hsl(var(--foreground))] mb-3">
                    Key Events
                  </h4>
                  <CanvasEventList
                    events={era.keyEvents}
                    accentColor={era.color}
                  />
                </div>
              )}

              {/* Key Figures */}
              {era.keyFigures && era.keyFigures.length > 0 && (
                <div>
                  <h4 className="text-sm font-semibold text-[hsl(var(--foreground))] mb-3">
                    Key Figures
                  </h4>
                  <CanvasFigureList
                    figures={era.keyFigures}
                    accentColor={era.color}
                  />
                </div>
              )}

              {/* Chat button */}
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onChatClick();
                }}
                className={cn(
                  "flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-medium",
                  "text-white transition-colors hover:opacity-90",
                  "focus:outline-none focus:ring-2 focus:ring-[hsl(var(--ring))] focus:ring-offset-2",
                )}
                style={{ backgroundColor: era.color }}
              >
                <MessageSquare className="h-4 w-4" />
                Chat about this era
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}
