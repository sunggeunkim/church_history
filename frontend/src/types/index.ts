export type User = {
  id: string;
  email: string;
  displayName: string;
  avatarUrl: string | null;
  createdAt: string;
};

export type Era = {
  id: number;
  name: string;
  slug: string;
  startYear: number;
  endYear: number | null;
  description: string;
  summary: string;
  color: string;
  order: number;
  keyEvents?: KeyEvent[];
  keyFigures?: KeyFigure[];
};

export type KeyEvent = {
  id: number;
  year: number;
  title: string;
  description: string;
};

export type KeyFigure = {
  id: number;
  name: string;
  birthYear: number | null;
  deathYear: number | null;
  title: string;
  description: string;
};

export type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
  createdAt: string;
  sources?: SourceCitation[];
};

export type ChatSession = {
  id: string;
  title: string;
  eraId: string | null;
  createdAt: string;
  updatedAt: string;
};

export type SourceCitation = {
  title: string;
  url: string;
  source: string;
};

export type Quiz = {
  id: number;
  era: number | null;
  eraName: string | null;
  difficulty: "beginner" | "intermediate" | "advanced";
  score: number;
  totalQuestions: number;
  percentageScore: number;
  passed: boolean;
  completedAt: string | null;
  createdAt: string;
  questions: QuizQuestionItem[];
};

export type QuizQuestionItem = {
  id: number;
  questionText: string;
  questionType: "mc" | "tf" | "sa";
  options: string[];
  userAnswer: string | null;
  correctAnswer: string | null;
  isCorrect: boolean | null;
  explanation: string;
  feedback: string | null;
  order: number;
};

export type QuizFeedback = {
  questionId: number;
  isCorrect: boolean;
  correctAnswer: string;
  explanation: string;
  feedback: string | null;
};

export type QuizHistoryItem = {
  id: number;
  era: number | null;
  eraName: string | null;
  difficulty: string;
  score: number;
  totalQuestions: number;
  percentageScore: number;
  passed: boolean;
  completedAt: string;
  createdAt: string;
};

export type QuizStats = {
  totalQuizzes: number;
  totalCompleted: number;
  averageScore: number;
  quizzesPassed: number;
  currentStreak: number;
  byEra: {
    eraId: number;
    eraName: string;
    quizzesCompleted: number;
    averageScore: number;
  }[];
};

export type ProgressSummary = {
  overall: {
    completionPercentage: number;
    erasVisited: number;
    erasChatted: number;
    erasQuizzed: number;
    totalEras: number;
  };
  stats: {
    totalQuizzes: number;
    quizzesPassed: number;
    averageScore: number;
    currentStreak: number;
    totalChatSessions: number;
    accountAgeDays: number;
  };
  byEra: EraProgress[];
  recentActivity: ActivityItem[];
};

export type EraProgress = {
  eraId: number;
  eraName: string;
  eraSlug: string;
  eraColor: string;
  eraVisited: boolean;
  firstVisitedAt: string | null;
  chatSessionsCount: number;
  lastChatAt: string | null;
  quizzesCompleted: number;
  quizzesPassed: number;
  bestQuizScore: number | null;
  lastQuizAt: string | null;
  completionPercentage: number;
};

export type ActivityItem = {
  type: "visit" | "chat" | "quiz";
  eraName: string;
  description: string;
  timestamp: string;
};

export type Achievement = {
  id: number;
  slug: string;
  name: string;
  description: string;
  category: string;
  iconKey: string;
  unlocked: boolean;
  unlockedAt: string | null;
};

export type AchievementList = {
  achievements: Achievement[];
  totalUnlocked: number;
  totalAchievements: number;
};
