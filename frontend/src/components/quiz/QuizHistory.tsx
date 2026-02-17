import { History } from "lucide-react";
import { QuizHistoryCard } from "./QuizHistoryCard";
import type { QuizHistoryItem } from "@/types";

type QuizHistoryProps = {
  quizzes: QuizHistoryItem[];
  onSelectQuiz: (quizId: number) => void;
};

export function QuizHistory({ quizzes, onSelectQuiz }: QuizHistoryProps) {
  if (quizzes.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-[hsl(var(--muted))] mb-4">
          <History className="w-8 h-8 text-[hsl(var(--muted-foreground))]" />
        </div>
        <h3 className="font-medium text-[hsl(var(--foreground))] mb-2">
          No Quiz History
        </h3>
        <p className="text-sm text-[hsl(var(--muted-foreground))]">
          Complete your first quiz to see your results here
        </p>
      </div>
    );
  }

  return (
    <div>
      <h2 className="font-heading text-xl font-bold text-[hsl(var(--foreground))] mb-4">
        Recent Quizzes
      </h2>
      <div className="space-y-3">
        {quizzes.slice(0, 10).map((quiz) => (
          <QuizHistoryCard
            key={quiz.id}
            quiz={quiz}
            onClick={() => onSelectQuiz(quiz.id)}
          />
        ))}
      </div>
    </div>
  );
}
