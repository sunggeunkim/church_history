import { useRef, useCallback } from "react";
import type { Era } from "@/types";
import { CanvasEraBlock } from "./CanvasEraBlock";

type CanvasTimelineProps = {
  eras: Era[];
  expandedEraId: number | null;
  selectedEraId: number | null;
  onToggleExpand: (eraId: number) => void;
  onChatClick: (era: Era) => void;
};

export function CanvasTimeline({
  eras,
  expandedEraId,
  selectedEraId,
  onToggleExpand,
  onChatClick,
}: CanvasTimelineProps) {
  const eraRefs = useRef<Map<number, HTMLDivElement>>(new Map());

  const setEraRef = useCallback(
    (eraId: number) => (el: HTMLDivElement | null) => {
      if (el) {
        eraRefs.current.set(eraId, el);
      } else {
        eraRefs.current.delete(eraId);
      }
    },
    [],
  );

  const sorted = [...eras].sort((a, b) => a.order - b.order);

  return (
    <div className="relative px-4 py-6">
      {/* SVG spine line */}
      <div className="absolute left-8 top-6 bottom-6 w-0.5 bg-[hsl(var(--border))]" />

      <div className="space-y-4 pl-8">
        {sorted.map((era) => (
          <div key={era.id} className="relative" ref={setEraRef(era.id)}>
            {/* Year marker on spine */}
            <div className="absolute -left-8 top-6 flex items-center">
              <div
                className="h-3 w-3 rounded-full border-2 border-[hsl(var(--background))]"
                style={{ backgroundColor: era.color }}
              />
            </div>

            <CanvasEraBlock
              era={era}
              isExpanded={expandedEraId === era.id}
              isSelected={selectedEraId === era.id}
              onToggle={() => onToggleExpand(era.id)}
              onChatClick={() => onChatClick(era)}
            />
          </div>
        ))}
      </div>
    </div>
  );
}
