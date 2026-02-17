import api from "./api";
import type { Quiz, QuizFeedback, QuizHistoryItem, QuizStats } from "@/types";

function mapQuiz(data: any): Quiz {
  return {
    id: data.id,
    era: data.era,
    eraName: data.era_name,
    difficulty: data.difficulty,
    score: data.score,
    totalQuestions: data.total_questions,
    percentageScore: data.percentage_score,
    passed: data.passed,
    completedAt: data.completed_at,
    createdAt: data.created_at,
    questions: data.questions.map((q: any) => ({
      id: q.id,
      questionText: q.question_text,
      questionType: q.question_type,
      options: q.options,
      userAnswer: q.user_answer,
      correctAnswer: q.correct_answer,
      isCorrect: q.is_correct,
      explanation: q.explanation,
      feedback: q.feedback,
      order: q.order,
    })),
  };
}

function mapQuizHistoryItem(data: any): QuizHistoryItem {
  return {
    id: data.id,
    era: data.era,
    eraName: data.era_name,
    difficulty: data.difficulty,
    score: data.score,
    totalQuestions: data.total_questions,
    percentageScore: data.percentage_score,
    passed: data.passed,
    completedAt: data.completed_at,
    createdAt: data.created_at,
  };
}

export async function createQuiz(
  eraId: number | null,
  difficulty: string,
  questionCount: number
): Promise<Quiz> {
  const response = await api.post("/quiz/quizzes/", {
    era_id: eraId,
    difficulty,
    question_count: questionCount,
  });
  return mapQuiz(response.data);
}

export async function fetchQuiz(quizId: number): Promise<Quiz> {
  const response = await api.get(`/quiz/quizzes/${quizId}/`);
  return mapQuiz(response.data);
}

export async function fetchQuizHistory(): Promise<QuizHistoryItem[]> {
  const response = await api.get("/quiz/quizzes/");
  return response.data.results.map(mapQuizHistoryItem);
}

export async function submitAnswer(
  quizId: number,
  questionId: number,
  answer: string
): Promise<QuizFeedback> {
  const response = await api.post(`/quiz/quizzes/${quizId}/submit_answer/`, {
    question_id: questionId,
    answer,
  });
  return {
    questionId: response.data.question_id,
    isCorrect: response.data.is_correct,
    correctAnswer: response.data.correct_answer,
    explanation: response.data.explanation,
    feedback: response.data.feedback,
  };
}

export async function completeQuiz(quizId: number): Promise<{
  score: number;
  totalQuestions: number;
  percentageScore: number;
  passed: boolean;
  completedAt: string;
}> {
  const response = await api.post(`/quiz/quizzes/${quizId}/complete/`);
  return {
    score: response.data.score,
    totalQuestions: response.data.total_questions,
    percentageScore: response.data.percentage_score,
    passed: response.data.passed,
    completedAt: response.data.completed_at,
  };
}

export async function fetchQuizStats(): Promise<QuizStats> {
  const response = await api.get("/quiz/stats/");
  return {
    totalQuizzes: response.data.total_quizzes,
    totalCompleted: response.data.total_completed,
    averageScore: response.data.average_score,
    quizzesPassed: response.data.quizzes_passed,
    currentStreak: response.data.current_streak,
    byEra: response.data.by_era.map((item: any) => ({
      eraId: item.era_id,
      eraName: item.era_name,
      quizzesCompleted: item.quizzes_completed,
      averageScore: item.average_score,
    })),
  };
}
