import { AchievementBadge } from "./AchievementBadge";
import type { Achievement } from "@/types";

type AchievementSectionProps = {
  achievements: Achievement[];
  totalUnlocked: number;
};

export function AchievementSection({ achievements, totalUnlocked }: AchievementSectionProps) {
  // Group achievements by category
  const groupedAchievements = achievements.reduce(
    (acc, achievement) => {
      if (!acc[achievement.category]) {
        acc[achievement.category] = [];
      }
      acc[achievement.category].push(achievement);
      return acc;
    },
    {} as Record<string, Achievement[]>,
  );

  const categoryLabels: Record<string, string> = {
    exploration: "Exploration",
    chat: "Chat",
    quiz: "Quiz",
    streak: "Streak",
    mastery: "Mastery",
  };

  const categoryOrder = ["exploration", "chat", "quiz", "streak", "mastery"];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="font-heading text-2xl font-bold text-[hsl(var(--foreground))]">
          Achievements
        </h2>
        <div className="text-sm text-[hsl(var(--muted-foreground))]">
          {totalUnlocked} of {achievements.length} unlocked
        </div>
      </div>

      {categoryOrder.map((category) => {
        const categoryAchievements = groupedAchievements[category];
        if (!categoryAchievements || categoryAchievements.length === 0) return null;

        const unlockedCount = categoryAchievements.filter((a) => a.unlocked).length;

        return (
          <div key={category}>
            <div className="mb-3 flex items-center justify-between">
              <h3 className="font-heading text-lg font-semibold text-[hsl(var(--foreground))]">
                {categoryLabels[category]}
              </h3>
              <span className="text-sm text-[hsl(var(--muted-foreground))]">
                {unlockedCount} / {categoryAchievements.length}
              </span>
            </div>
            <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
              {categoryAchievements.map((achievement) => (
                <AchievementBadge key={achievement.id} achievement={achievement} />
              ))}
            </div>
          </div>
        );
      })}
    </div>
  );
}
