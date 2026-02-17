import { Check, X } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { cn } from "@/lib/utils";
import type { EraProgress } from "@/types";

type EraProgressCardProps = {
  progress: EraProgress;
};

export function EraProgressCard({ progress }: EraProgressCardProps) {
  const navigate = useNavigate();

  return (
    <div
      className="rounded-lg border-2 bg-[hsl(var(--card))] p-4 transition-shadow hover:shadow-md"
      style={{ borderTopColor: progress.eraColor, borderTopWidth: "4px" }}
    >
      {/* Era name */}
      <h3 className="font-heading text-lg font-bold text-[hsl(var(--foreground))]">
        {progress.eraName}
      </h3>

      {/* Checkmark indicators */}
      <div className="mt-4 flex items-center gap-4">
        <div className="flex items-center gap-1">
          {progress.eraVisited ? (
            <Check className="h-5 w-5 text-green-600 dark:text-green-400" />
          ) : (
            <X className="h-5 w-5 text-[hsl(var(--muted-foreground))]" />
          )}
          <span className="text-sm text-[hsl(var(--muted-foreground))]">Visited</span>
        </div>

        <div className="flex items-center gap-1">
          {progress.chatSessionsCount > 0 ? (
            <Check className="h-5 w-5 text-green-600 dark:text-green-400" />
          ) : (
            <X className="h-5 w-5 text-[hsl(var(--muted-foreground))]" />
          )}
          <span className="text-sm text-[hsl(var(--muted-foreground))]">Chatted</span>
        </div>

        <div className="flex items-center gap-1">
          {progress.quizzesPassed > 0 ? (
            <Check className="h-5 w-5 text-green-600 dark:text-green-400" />
          ) : (
            <X className="h-5 w-5 text-[hsl(var(--muted-foreground))]" />
          )}
          <span className="text-sm text-[hsl(var(--muted-foreground))]">Quizzed</span>
        </div>
      </div>

      {/* Best quiz score */}
      {progress.bestQuizScore !== null && (
        <div className="mt-3">
          <span className="text-sm text-[hsl(var(--muted-foreground))]">Best Score: </span>
          <span className="text-sm font-semibold text-[hsl(var(--foreground))]">
            {progress.bestQuizScore}%
          </span>
        </div>
      )}

      {/* Completion bar */}
      <div className="mt-4">
        <div className="mb-1 flex items-center justify-between">
          <span className="text-sm text-[hsl(var(--muted-foreground))]">Completion</span>
          <span className="text-sm font-semibold text-[hsl(var(--foreground))]">
            {progress.completionPercentage}%
          </span>
        </div>
        <div className="h-2 overflow-hidden rounded-full bg-[hsl(var(--muted))]">
          <div
            className="h-full rounded-full transition-all duration-500"
            style={{
              width: `${progress.completionPercentage}%`,
              backgroundColor: progress.eraColor,
            }}
          />
        </div>
      </div>

      {/* Action button */}
      <button
        onClick={() => navigate(`/canvas?era=${progress.eraSlug}`)}
        className={cn(
          "mt-4 w-full rounded-lg px-4 py-2 text-sm font-medium text-white transition-opacity hover:opacity-90",
          "focus:outline-none focus:ring-2 focus:ring-[hsl(var(--ring))] focus:ring-offset-2",
        )}
        style={{ backgroundColor: progress.eraColor }}
      >
        Explore Era
      </button>
    </div>
  );
}
