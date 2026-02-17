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
  totalEras: number;
  completedEras: number;
  quizzesPassed: number;
  currentStreak: number;
  overallPercent: number;
};
