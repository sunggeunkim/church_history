import { cn } from "@/lib/utils";
import { Calendar, Trophy, Award } from "lucide-react";
import type { QuizHistoryItem } from "@/types";

type QuizHistoryCardProps = {
  quiz: QuizHistoryItem;
  onClick: () => void;
};

export function QuizHistoryCard({ quiz, onClick }: QuizHistoryCardProps) {
  const formattedDate = new Date(quiz.completedAt).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });

  return (
    <button
      onClick={onClick}
      className={cn(
        "w-full text-left p-4 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--card))]",
        "hover:bg-[hsl(var(--muted))] transition-colors",
        "focus:outline-none focus:ring-2 focus:ring-[hsl(var(--ring))] focus:ring-offset-2"
      )}
    >
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-2">
            <h3 className="font-medium text-[hsl(var(--foreground))] truncate">
              {quiz.eraName || "All Eras"}
            </h3>
            <span className="flex-shrink-0 px-2 py-0.5 rounded-full text-xs font-medium bg-[hsl(var(--muted))] text-[hsl(var(--muted-foreground))]">
              {quiz.difficulty.charAt(0).toUpperCase() + quiz.difficulty.slice(1)}
            </span>
          </div>

          <div className="flex items-center gap-4 text-sm text-[hsl(var(--muted-foreground))]">
            <div className="flex items-center gap-1">
              <Calendar className="w-3.5 h-3.5" />
              <span>{formattedDate}</span>
            </div>
            <div className="flex items-center gap-1">
              <Trophy className="w-3.5 h-3.5" />
              <span>{quiz.score}/{quiz.totalQuestions}</span>
            </div>
          </div>
        </div>

        <div className="flex-shrink-0 text-right">
          <div className={cn(
            "text-2xl font-bold mb-1",
            quiz.passed ? "text-green-600 dark:text-green-400" : "text-orange-600 dark:text-orange-400"
          )}>
            {quiz.percentageScore}%
          </div>
          <div className={cn(
            "inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold",
            quiz.passed
              ? "bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200"
              : "bg-orange-100 dark:bg-orange-900 text-orange-800 dark:text-orange-200"
          )}>
            <Award className="w-3 h-3" />
            {quiz.passed ? "Passed" : "Failed"}
          </div>
        </div>
      </div>
    </button>
  );
}
