export type User = {
  id: string;
  email: string;
  displayName: string;
  avatarUrl: string | null;
  createdAt: string;
};

export type Era = {
  id: string;
  name: string;
  slug: string;
  startYear: number;
  endYear: number | null;
  description: string;
  color: string;
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

export type QuizQuestion = {
  id: string;
  question: string;
  options: string[];
  correctIndex: number;
  explanation: string;
};

export type ProgressSummary = {
  totalEras: number;
  completedEras: number;
  quizzesPassed: number;
  currentStreak: number;
  overallPercent: number;
};
