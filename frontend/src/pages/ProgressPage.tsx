import { useEffect } from "react";
import { Loader2, AlertCircle } from "lucide-react";
import { useProgressStore } from "@/stores/progressStore";
import { ProgressRing } from "@/components/progress/ProgressRing";
import { StatsOverview } from "@/components/progress/StatsOverview";
import { EraProgressGrid } from "@/components/progress/EraProgressGrid";
import { AchievementSection } from "@/components/progress/AchievementSection";
import { RecentActivity } from "@/components/progress/RecentActivity";
import { ShareButton } from "@/components/sharing/ShareButton";

export function ProgressPage() {
  const { summary, achievements, isLoading, isLoadingAchievements, error, loadSummary, loadAchievements } =
    useProgressStore();

  useEffect(() => {
    loadSummary();
    loadAchievements();
  }, [loadSummary, loadAchievements]);

  if (isLoading && !summary) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="text-center">
          <Loader2 className="mx-auto h-8 w-8 animate-spin text-[hsl(var(--muted-foreground))]" />
          <p className="mt-4 text-sm text-[hsl(var(--muted-foreground))]">Loading progress...</p>
        </div>
      </div>
    );
  }

  if (error && !summary) {
    return (
      <div className="flex h-full items-center justify-center px-4">
        <div className="rounded-lg border border-red-200 bg-red-50 dark:border-red-900 dark:bg-red-950 p-6 text-center">
          <AlertCircle className="mx-auto h-8 w-8 text-red-600 dark:text-red-400" />
          <p className="mt-2 text-sm text-red-800 dark:text-red-200">{error}</p>
        </div>
      </div>
    );
  }

  if (!summary) {
    return null;
  }

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto space-y-8">
      {/* Header with Progress Ring */}
      <div className="flex flex-col items-center gap-6 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="font-heading text-3xl font-bold tracking-tight text-[hsl(var(--foreground))]">
              Your Progress
            </h1>
            <ShareButton
              shareType="progress"
              variant="button"
              label="Share Progress"
            />
          </div>
          <p className="mt-2 text-[hsl(var(--muted-foreground))]">
            Track your learning journey across all eras
          </p>
        </div>
        <ProgressRing percentage={summary.overall.completionPercentage} />
      </div>

      {/* Stats Overview */}
      <section>
        <h2 className="font-heading text-2xl font-bold text-[hsl(var(--foreground))] mb-4">
          Statistics
        </h2>
        <StatsOverview
          erasVisited={summary.overall.erasVisited}
          totalChatSessions={summary.stats.totalChatSessions}
          totalQuizzes={summary.stats.totalQuizzes}
          averageScore={summary.stats.averageScore}
          currentStreak={summary.stats.currentStreak}
          accountAgeDays={summary.stats.accountAgeDays}
        />
      </section>

      {/* Era Progress Grid */}
      <section>
        <h2 className="font-heading text-2xl font-bold text-[hsl(var(--foreground))] mb-4">
          Progress by Era
        </h2>
        <EraProgressGrid eraProgress={summary.byEra} />
      </section>

      {/* Achievements */}
      {!isLoadingAchievements && achievements.length > 0 && (
        <section>
          <AchievementSection
            achievements={achievements}
            totalUnlocked={achievements.filter((a) => a.unlocked).length}
          />
        </section>
      )}

      {/* Recent Activity */}
      <section>
        <h2 className="font-heading text-2xl font-bold text-[hsl(var(--foreground))] mb-4">
          Recent Activity
        </h2>
        <RecentActivity activities={summary.recentActivity} />
      </section>
    </div>
  );
}
