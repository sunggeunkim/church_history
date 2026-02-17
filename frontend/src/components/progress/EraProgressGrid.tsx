import { EraProgressCard } from "./EraProgressCard";
import type { EraProgress } from "@/types";

type EraProgressGridProps = {
  eraProgress: EraProgress[];
};

export function EraProgressGrid({ eraProgress }: EraProgressGridProps) {
  if (eraProgress.length === 0) {
    return (
      <div className="rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-6 text-center">
        <p className="text-[hsl(var(--muted-foreground))]">No era progress data available.</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {eraProgress.map((progress) => (
        <EraProgressCard key={progress.eraId} progress={progress} />
      ))}
    </div>
  );
}
