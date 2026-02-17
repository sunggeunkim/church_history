import { useMemo } from "react";
import type { Era } from "@/types";
import { cn } from "@/lib/utils";

type TimelineProps = {
  eras: Era[];
  selectedEra: Era | null;
  onEraClick: (era: Era) => void;
};

export function Timeline({ eras, selectedEra, onEraClick }: TimelineProps) {
  const sortedEras = useMemo(
    () => [...eras].sort((a, b) => a.order - b.order),
    [eras]
  );

  // Calculate total duration and proportions
  const { totalDuration, eraProportions } = useMemo(() => {
    const currentYear = new Date().getFullYear();
    let total = 0;
    const proportions: number[] = [];

    sortedEras.forEach((era) => {
      const duration = (era.endYear ?? currentYear) - era.startYear;
      total += duration;
      proportions.push(duration);
    });

    return {
      totalDuration: total,
      eraProportions: proportions.map((d) => (d / total) * 100),
    };
  }, [sortedEras]);

  return (
    <div className="w-full overflow-x-auto pb-4">
      <div className="min-w-[800px]">
        {/* Era names */}
        <div className="flex mb-2">
          {sortedEras.map((era, index) => (
            <div
              key={era.id}
              style={{ width: `${eraProportions[index]}%` }}
              className="px-2 text-center"
            >
              <h3 className="font-heading text-sm font-semibold text-[hsl(var(--foreground))] truncate">
                {era.name}
              </h3>
            </div>
          ))}
        </div>

        {/* Timeline bar */}
        <div className="flex h-16 rounded-lg overflow-hidden shadow-sm">
          {sortedEras.map((era, index) => (
            <button
              key={era.id}
              style={{
                width: `${eraProportions[index]}%`,
                backgroundColor: era.color,
              }}
              className={cn(
                "relative transition-all duration-200 hover:brightness-110 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500",
                selectedEra?.id === era.id && "brightness-110 ring-2 ring-offset-2 ring-white dark:ring-offset-gray-900"
              )}
              onClick={() => onEraClick(era)}
              aria-label={`Select ${era.name} era`}
            >
              <div className="absolute inset-0 bg-gradient-to-b from-white/10 to-transparent" />
            </button>
          ))}
        </div>

        {/* Year ranges */}
        <div className="flex mt-2">
          {sortedEras.map((era, index) => (
            <div
              key={era.id}
              style={{ width: `${eraProportions[index]}%` }}
              className="px-2 text-center"
            >
              <p className="text-xs text-[hsl(var(--muted-foreground))]">
                {era.startYear}–{era.endYear ?? "present"}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
