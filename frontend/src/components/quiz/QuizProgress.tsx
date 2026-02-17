import { cn } from "@/lib/utils";

type QuizProgressProps = {
  currentQuestion: number;
  totalQuestions: number;
  eraName: string | null;
  difficulty: string;
};

export function QuizProgress({ currentQuestion, totalQuestions, eraName, difficulty }: QuizProgressProps) {
  const percentage = ((currentQuestion + 1) / totalQuestions) * 100;

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-[hsl(var(--muted-foreground))]">
            {eraName || "All Eras"}
          </p>
          <p className="text-xs text-[hsl(var(--muted-foreground))]">
            <span className={cn(
              "inline-block px-2 py-0.5 rounded-full text-xs font-medium",
              "bg-[hsl(var(--muted))] text-[hsl(var(--muted-foreground))]"
            )}>
              {difficulty.charAt(0).toUpperCase() + difficulty.slice(1)}
            </span>
          </p>
        </div>
        <div className="text-right">
          <p className="text-sm font-medium text-[hsl(var(--foreground))]">
            Question {currentQuestion + 1} of {totalQuestions}
          </p>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="h-2 bg-[hsl(var(--muted))] rounded-full overflow-hidden">
        <div
          className="h-full bg-primary-600 dark:bg-primary-500 transition-all duration-300"
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}
