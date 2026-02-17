import { useMemo } from "react";
import type { Era } from "@/types";
import { cn } from "@/lib/utils";

type CanvasOverviewBarProps = {
  eras: Era[];
  selectedEraId: number | null;
  onEraClick: (era: Era) => void;
};

export function CanvasOverviewBar({
  eras,
  selectedEraId,
  onEraClick,
}: CanvasOverviewBarProps) {
  const sortedEras = useMemo(
    () => [...eras].sort((a, b) => a.order - b.order),
    [eras],
  );

  const eraProportions = useMemo(() => {
    const currentYear = new Date().getFullYear();
    const durations = sortedEras.map(
      (era) => (era.endYear ?? currentYear) - era.startYear,
    );
    const total = durations.reduce((sum, d) => sum + d, 0);
    return durations.map((d) => (d / total) * 100);
  }, [sortedEras]);

  return (
    <div className="sticky top-0 z-10 border-b border-[hsl(var(--border))] bg-[hsl(var(--background))] px-4 py-3">
      <div className="flex h-8 overflow-hidden rounded-lg">
        {sortedEras.map((era, index) => (
          <button
            key={era.id}
            style={{
              width: `${eraProportions[index]}%`,
              backgroundColor: era.color,
            }}
            className={cn(
              "relative transition-all duration-200 hover:brightness-110",
              "focus:outline-none focus:ring-2 focus:ring-inset focus:ring-white/50",
              selectedEraId === era.id &&
                "brightness-110 ring-2 ring-inset ring-white/70",
            )}
            onClick={() => onEraClick(era)}
            aria-label={`Navigate to ${era.name}`}
            role="tab"
            aria-selected={selectedEraId === era.id}
          >
            <span className="absolute inset-0 flex items-center justify-center text-[10px] font-medium text-white/90 truncate px-1">
              {eraProportions[index] > 12 ? era.name : ""}
            </span>
          </button>
        ))}
      </div>
      <div className="mt-1 flex">
        {sortedEras.map((era, index) => (
          <div
            key={era.id}
            style={{ width: `${eraProportions[index]}%` }}
            className="text-center"
          >
            <span className="text-[10px] text-[hsl(var(--muted-foreground))]">
              {eraProportions[index] > 8
                ? `${era.startYear}–${era.endYear ?? "now"}`
                : ""}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
