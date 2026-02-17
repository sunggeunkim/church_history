import api from "./api";
import type { ProgressSummary, EraProgress, Achievement, ActivityItem } from "@/types";

type ProgressSummaryResponse = {
  overall: {
    completion_percentage: number;
    eras_visited: number;
    eras_chatted: number;
    eras_quizzed: number;
    total_eras: number;
  };
  stats: {
    total_quizzes: number;
    quizzes_passed: number;
    average_score: number;
    current_streak: number;
    total_chat_sessions: number;
    account_age_days: number;
  };
  by_era: any[];
  recent_activity: any[];
};

export async function fetchProgressSummary(): Promise<ProgressSummary> {
  const response = await api.get<ProgressSummaryResponse>("/progress/summary/");
  const data = response.data;

  return {
    overall: {
      completionPercentage: data.overall.completion_percentage,
      erasVisited: data.overall.eras_visited,
      erasChatted: data.overall.eras_chatted,
      erasQuizzed: data.overall.eras_quizzed,
      totalEras: data.overall.total_eras,
    },
    stats: {
      totalQuizzes: data.stats.total_quizzes,
      quizzesPassed: data.stats.quizzes_passed,
      averageScore: data.stats.average_score,
      currentStreak: data.stats.current_streak,
      totalChatSessions: data.stats.total_chat_sessions,
      accountAgeDays: data.stats.account_age_days,
    },
    byEra: data.by_era.map((ep: any): EraProgress => ({
      eraId: ep.era_id,
      eraName: ep.era_name,
      eraSlug: ep.era_slug,
      eraColor: ep.era_color,
      eraVisited: ep.era_visited,
      firstVisitedAt: ep.first_visited_at,
      chatSessionsCount: ep.chat_sessions_count,
      lastChatAt: ep.last_chat_at,
      quizzesCompleted: ep.quizzes_completed,
      quizzesPassed: ep.quizzes_passed,
      bestQuizScore: ep.best_quiz_score,
      lastQuizAt: ep.last_quiz_at,
      completionPercentage: ep.completion_percentage,
    })),
    recentActivity: data.recent_activity.map((item: any): ActivityItem => ({
      type: item.type,
      eraName: item.era_name,
      description: item.description,
      timestamp: item.timestamp,
    })),
  };
}

export async function markEraVisited(eraId: number): Promise<{
  eraId: number;
  eraVisited: boolean;
  firstVisitedAt: string;
  completionPercentage: number;
}> {
  const response = await api.post("/progress/mark-era-visited/", {
    era_id: eraId,
  });
  return {
    eraId: response.data.era_id,
    eraVisited: response.data.era_visited,
    firstVisitedAt: response.data.first_visited_at,
    completionPercentage: response.data.completion_percentage,
  };
}

export async function fetchAchievements(): Promise<{
  achievements: Achievement[];
  totalUnlocked: number;
  totalAchievements: number;
}> {
  const response = await api.get("/progress/achievements/");
  return {
    achievements: response.data.achievements.map((a: any): Achievement => ({
      id: a.id,
      slug: a.slug,
      name: a.name,
      description: a.description,
      category: a.category,
      iconKey: a.icon_key,
      unlocked: a.unlocked,
      unlockedAt: a.unlocked_at,
    })),
    totalUnlocked: response.data.total_unlocked,
    totalAchievements: response.data.total_achievements,
  };
}

export async function checkAchievements(): Promise<{
  newlyUnlocked: Achievement[];
  totalUnlocked: number;
}> {
  const response = await api.post("/progress/check-achievements/");
  return {
    newlyUnlocked: response.data.newly_unlocked.map((a: any): Achievement => ({
      id: a.id,
      slug: a.slug,
      name: a.name,
      description: a.description,
      category: a.category,
      iconKey: a.icon_key,
      unlocked: true,
      unlockedAt: a.unlocked_at,
    })),
    totalUnlocked: response.data.total_unlocked,
  };
}
