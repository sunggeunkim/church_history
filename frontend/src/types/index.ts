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
