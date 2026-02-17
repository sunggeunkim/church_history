import * as Icons from "lucide-react";
import { Lock } from "lucide-react";
import { cn } from "@/lib/utils";
import type { Achievement } from "@/types";

type AchievementBadgeProps = {
  achievement: Achievement;
};

const getCategoryColor = (category: string) => {
  switch (category) {
    case "exploration":
      return "bg-blue-100 dark:bg-blue-900 border-blue-300 dark:border-blue-700";
    case "chat":
      return "bg-purple-100 dark:bg-purple-900 border-purple-300 dark:border-purple-700";
    case "quiz":
      return "bg-green-100 dark:bg-green-900 border-green-300 dark:border-green-700";
    case "streak":
      return "bg-orange-100 dark:bg-orange-900 border-orange-300 dark:border-orange-700";
    case "mastery":
      return "bg-yellow-100 dark:bg-yellow-900 border-yellow-300 dark:border-yellow-700";
    default:
      return "bg-[hsl(var(--muted))] border-[hsl(var(--border))]";
  }
};

function kebabToPascal(str: string) {
  return str
    .split("-")
    .map((s) => s.charAt(0).toUpperCase() + s.slice(1))
    .join("");
}

export function AchievementBadge({ achievement }: AchievementBadgeProps) {
  const IconComponent =
    (Icons as any)[kebabToPascal(achievement.iconKey)] || Icons.Award;

  return (
    <div
      className={cn(
        "relative rounded-lg border-2 p-4 transition-all",
        achievement.unlocked
          ? getCategoryColor(achievement.category)
          : "border-[hsl(var(--border))] bg-[hsl(var(--muted))] opacity-60",
        achievement.unlocked && "hover:scale-105",
      )}
    >
      {/* Lock overlay for locked achievements */}
      {!achievement.unlocked && (
        <div className="absolute right-2 top-2">
          <Lock className="h-4 w-4 text-[hsl(var(--muted-foreground))]" />
        </div>
      )}

      {/* Icon */}
      <div className="flex justify-center">
        <div
          className={cn(
            "rounded-full p-3",
            achievement.unlocked
              ? "bg-white dark:bg-gray-800"
              : "bg-[hsl(var(--background))]",
          )}
        >
          <IconComponent
            className={cn(
              "h-8 w-8",
              achievement.unlocked
                ? "text-[hsl(var(--foreground))]"
                : "text-[hsl(var(--muted-foreground))]",
            )}
          />
        </div>
      </div>

      {/* Name */}
      <h4
        className={cn(
          "mt-3 text-center font-heading text-sm font-semibold",
          achievement.unlocked
            ? "text-[hsl(var(--foreground))]"
            : "text-[hsl(var(--muted-foreground))]",
        )}
      >
        {achievement.name}
      </h4>

      {/* Description */}
      <p className="mt-1 text-center text-xs text-[hsl(var(--muted-foreground))]">
        {achievement.description}
      </p>

      {/* Unlock date */}
      {achievement.unlocked && achievement.unlockedAt && (
        <p className="mt-2 text-center text-xs text-[hsl(var(--muted-foreground))]">
          Unlocked: {new Date(achievement.unlockedAt).toLocaleDateString()}
        </p>
      )}
    </div>
  );
}
