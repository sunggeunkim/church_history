import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import type { ProgressSummary, Achievement, EraProgress, ActivityItem } from "@/types";

// Mock the stores before importing components
vi.mock("@/stores/progressStore", () => ({
  useProgressStore: vi.fn(),
}));

vi.mock("@/hooks/useWindowSize", () => ({
  useWindowSize: vi.fn(() => ({ width: 1024, height: 768 })),
}));

vi.mock("react-confetti", () => ({
  default: () => null,
}));

import { useProgressStore } from "@/stores/progressStore";

const mockEraProgress: EraProgress = {
  eraId: 1,
  eraName: "Early Church",
  eraSlug: "early-church",
  eraColor: "#C2410C",
  eraVisited: true,
  firstVisitedAt: "2026-02-01T10:00:00Z",
  chatSessionsCount: 3,
  lastChatAt: "2026-02-15T14:30:00Z",
  quizzesCompleted: 2,
  quizzesPassed: 2,
  bestQuizScore: 90,
  lastQuizAt: "2026-02-16T09:00:00Z",
  completionPercentage: 100,
};

const mockActivity: ActivityItem = {
  type: "quiz",
  eraName: "Early Church",
  description: "Completed quiz with 90%",
  timestamp: "2026-02-16T09:00:00Z",
};

const mockAchievement: Achievement = {
  id: 1,
  slug: "first-visit",
  name: "First Steps",
  description: "Explore your first era on the canvas",
  category: "exploration",
  iconKey: "Map",
  unlocked: true,
  unlockedAt: "2026-02-01T10:00:00Z",
};

const mockSummary: ProgressSummary = {
  overall: {
    completionPercentage: 50,
    erasVisited: 4,
    erasChatted: 3,
    erasQuizzed: 2,
    totalEras: 6,
  },
  stats: {
    totalQuizzes: 15,
    quizzesPassed: 12,
    averageScore: 78.5,
    currentStreak: 3,
    totalChatSessions: 24,
    accountAgeDays: 45,
  },
  byEra: [mockEraProgress],
  recentActivity: [mockActivity],
};

const defaultProgressStore = {
  summary: null,
  achievements: [],
  newlyUnlocked: [],
  isLoading: false,
  isLoadingAchievements: false,
  error: null,
  loadSummary: vi.fn(),
  loadAchievements: vi.fn(),
  markEraVisited: vi.fn(),
  checkAchievements: vi.fn(),
  clearNewlyUnlocked: vi.fn(),
  clearError: vi.fn(),
};

function renderWithRouter(ui: React.ReactElement) {
  return render(<BrowserRouter>{ui}</BrowserRouter>);
}

describe("Progress Components", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    (useProgressStore as unknown as ReturnType<typeof vi.fn>).mockReturnValue(defaultProgressStore);
  });

  describe("ProgressRing", () => {
    it("renders with correct percentage", async () => {
      const { ProgressRing } = await import("@/components/progress/ProgressRing");
      render(<ProgressRing percentage={75} />);

      expect(screen.getByText("75%")).toBeInTheDocument();
      expect(screen.getByText("Complete")).toBeInTheDocument();
    });

    it("renders with 0 percentage", async () => {
      const { ProgressRing } = await import("@/components/progress/ProgressRing");
      render(<ProgressRing percentage={0} />);

      expect(screen.getByText("0%")).toBeInTheDocument();
    });

    it("renders with 100 percentage", async () => {
      const { ProgressRing } = await import("@/components/progress/ProgressRing");
      render(<ProgressRing percentage={100} />);

      expect(screen.getByText("100%")).toBeInTheDocument();
    });
  });

  describe("StatsOverview", () => {
    it("renders all stat cards", async () => {
      const { StatsOverview } = await import("@/components/progress/StatsOverview");
      render(
        <StatsOverview
          erasVisited={4}
          totalChatSessions={24}
          totalQuizzes={15}
          averageScore={78.5}
          currentStreak={3}
          accountAgeDays={45}
        />
      );

      expect(screen.getByText("Eras Explored")).toBeInTheDocument();
      expect(screen.getByText("Chat Sessions")).toBeInTheDocument();
      expect(screen.getByText("Quizzes Taken")).toBeInTheDocument();
      expect(screen.getByText("Average Score")).toBeInTheDocument();
      expect(screen.getByText("Current Streak")).toBeInTheDocument();
      expect(screen.getByText("Days Learning")).toBeInTheDocument();
    });
  });

  describe("EraProgressCard", () => {
    it("renders era name and checkmarks", async () => {
      const { EraProgressCard } = await import("@/components/progress/EraProgressCard");
      renderWithRouter(<EraProgressCard progress={mockEraProgress} />);

      expect(screen.getByText("Early Church")).toBeInTheDocument();
      expect(screen.getByText("Visited")).toBeInTheDocument();
      expect(screen.getByText("Chatted")).toBeInTheDocument();
      expect(screen.getByText("Quizzed")).toBeInTheDocument();
    });

    it("displays best quiz score", async () => {
      const { EraProgressCard } = await import("@/components/progress/EraProgressCard");
      renderWithRouter(<EraProgressCard progress={mockEraProgress} />);

      expect(screen.getByText("Best Score:")).toBeInTheDocument();
      expect(screen.getByText("90%")).toBeInTheDocument();
    });

    it("displays completion percentage", async () => {
      const { EraProgressCard } = await import("@/components/progress/EraProgressCard");
      renderWithRouter(<EraProgressCard progress={mockEraProgress} />);

      expect(screen.getByText("Completion")).toBeInTheDocument();
      expect(screen.getByText("100%")).toBeInTheDocument();
    });

    it("renders explore button", async () => {
      const { EraProgressCard } = await import("@/components/progress/EraProgressCard");
      renderWithRouter(<EraProgressCard progress={mockEraProgress} />);

      expect(screen.getByRole("button", { name: "Explore Era" })).toBeInTheDocument();
    });
  });

  describe("EraProgressGrid", () => {
    it("renders era progress cards", async () => {
      const { EraProgressGrid } = await import("@/components/progress/EraProgressGrid");
      renderWithRouter(<EraProgressGrid eraProgress={[mockEraProgress]} />);

      expect(screen.getAllByText("Early Church").length).toBeGreaterThan(0);
    });

    it("renders empty state when no progress", async () => {
      const { EraProgressGrid } = await import("@/components/progress/EraProgressGrid");
      render(<EraProgressGrid eraProgress={[]} />);

      expect(screen.getByText("No era progress data available.")).toBeInTheDocument();
    });
  });

  describe("AchievementBadge", () => {
    it("renders unlocked achievement", async () => {
      const { AchievementBadge } = await import("@/components/progress/AchievementBadge");
      render(<AchievementBadge achievement={mockAchievement} />);

      expect(screen.getByText("First Steps")).toBeInTheDocument();
      expect(screen.getByText("Explore your first era on the canvas")).toBeInTheDocument();
      expect(screen.getByText(/unlocked/i)).toBeInTheDocument();
    });

    it("renders locked achievement", async () => {
      const { AchievementBadge } = await import("@/components/progress/AchievementBadge");
      const lockedAchievement = { ...mockAchievement, unlocked: false, unlockedAt: null };
      render(<AchievementBadge achievement={lockedAchievement} />);

      expect(screen.getByText("First Steps")).toBeInTheDocument();
      expect(screen.queryByText(/unlocked/i)).not.toBeInTheDocument();
    });
  });

  describe("AchievementSection", () => {
    it("renders achievement section with count", async () => {
      const { AchievementSection } = await import("@/components/progress/AchievementSection");
      render(<AchievementSection achievements={[mockAchievement]} totalUnlocked={1} />);

      expect(screen.getByText("Achievements")).toBeInTheDocument();
      expect(screen.getByText("1 of 1 unlocked")).toBeInTheDocument();
    });

    it("groups achievements by category", async () => {
      const { AchievementSection } = await import("@/components/progress/AchievementSection");
      const chatAchievement = {
        ...mockAchievement,
        id: 2,
        category: "chat",
        name: "Chat Master",
      };
      render(
        <AchievementSection
          achievements={[mockAchievement, chatAchievement]}
          totalUnlocked={2}
        />
      );

      expect(screen.getByText("Exploration")).toBeInTheDocument();
      expect(screen.getByText("Chat")).toBeInTheDocument();
    });
  });

  describe("RecentActivity", () => {
    it("renders activity items", async () => {
      const { RecentActivity } = await import("@/components/progress/RecentActivity");
      render(<RecentActivity activities={[mockActivity]} />);

      expect(screen.getByText("Early Church")).toBeInTheDocument();
      expect(screen.getByText(/completed quiz with 90%/i)).toBeInTheDocument();
    });

    it("renders empty state when no activities", async () => {
      const { RecentActivity } = await import("@/components/progress/RecentActivity");
      render(<RecentActivity activities={[]} />);

      expect(screen.getByText("No recent activity yet.")).toBeInTheDocument();
    });

    it("limits to 10 activities", async () => {
      const { RecentActivity } = await import("@/components/progress/RecentActivity");
      const manyActivities = Array(15)
        .fill(null)
        .map((_, i) => ({ ...mockActivity, description: `Activity ${i}` }));
      const { container } = render(<RecentActivity activities={manyActivities} />);

      const activityItems = container.querySelectorAll(".flex.items-start.gap-3");
      expect(activityItems.length).toBeLessThanOrEqual(10);
    });
  });

  describe("ProgressPage", () => {
    it("renders loading state", async () => {
      (useProgressStore as unknown as ReturnType<typeof vi.fn>).mockReturnValue({
        ...defaultProgressStore,
        isLoading: true,
        summary: null,
      });

      const { ProgressPage } = await import("@/pages/ProgressPage");
      renderWithRouter(<ProgressPage />);

      expect(screen.getByText("Loading progress...")).toBeInTheDocument();
    });

    it("renders error state", async () => {
      (useProgressStore as unknown as ReturnType<typeof vi.fn>).mockReturnValue({
        ...defaultProgressStore,
        error: "Network error",
        summary: null,
      });

      const { ProgressPage } = await import("@/pages/ProgressPage");
      renderWithRouter(<ProgressPage />);

      expect(screen.getByText("Network error")).toBeInTheDocument();
    });

    it("renders all sections when data loaded", async () => {
      (useProgressStore as unknown as ReturnType<typeof vi.fn>).mockReturnValue({
        ...defaultProgressStore,
        summary: mockSummary,
        achievements: [mockAchievement],
      });

      const { ProgressPage } = await import("@/pages/ProgressPage");
      renderWithRouter(<ProgressPage />);

      expect(screen.getByText("Your Progress")).toBeInTheDocument();
      expect(screen.getByText("Statistics")).toBeInTheDocument();
      expect(screen.getByText("Progress by Era")).toBeInTheDocument();
      expect(screen.getByText("Achievements")).toBeInTheDocument();
      expect(screen.getByText("Recent Activity")).toBeInTheDocument();
    });

    it("calls loadSummary and loadAchievements on mount", async () => {
      const loadSummary = vi.fn();
      const loadAchievements = vi.fn();
      (useProgressStore as unknown as ReturnType<typeof vi.fn>).mockReturnValue({
        ...defaultProgressStore,
        loadSummary,
        loadAchievements,
      });

      const { ProgressPage } = await import("@/pages/ProgressPage");
      renderWithRouter(<ProgressPage />);

      await waitFor(() => {
        expect(loadSummary).toHaveBeenCalled();
        expect(loadAchievements).toHaveBeenCalled();
      });
    });

    it("renders progress ring with completion percentage", async () => {
      (useProgressStore as unknown as ReturnType<typeof vi.fn>).mockReturnValue({
        ...defaultProgressStore,
        summary: mockSummary,
      });

      const { ProgressPage } = await import("@/pages/ProgressPage");
      renderWithRouter(<ProgressPage />);

      expect(screen.getByText("50%")).toBeInTheDocument();
    });

    it("renders stats overview", async () => {
      (useProgressStore as unknown as ReturnType<typeof vi.fn>).mockReturnValue({
        ...defaultProgressStore,
        summary: mockSummary,
      });

      const { ProgressPage } = await import("@/pages/ProgressPage");
      renderWithRouter(<ProgressPage />);

      expect(screen.getByText("Eras Explored")).toBeInTheDocument();
      expect(screen.getByText("Chat Sessions")).toBeInTheDocument();
    });

    it("renders era progress grid", async () => {
      (useProgressStore as unknown as ReturnType<typeof vi.fn>).mockReturnValue({
        ...defaultProgressStore,
        summary: mockSummary,
      });

      const { ProgressPage } = await import("@/pages/ProgressPage");
      renderWithRouter(<ProgressPage />);

      expect(screen.getAllByText("Early Church").length).toBeGreaterThan(0);
    });
  });
});
