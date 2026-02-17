import { useState } from "react";
import { useEraStore } from "@/stores/eraStore";
import { cn } from "@/lib/utils";
import { Brain } from "lucide-react";

type QuizSetupProps = {
  onStartQuiz: (eraId: number | null, difficulty: string, questionCount: number) => void;
  isLoading: boolean;
};

export function QuizSetup({ onStartQuiz, isLoading }: QuizSetupProps) {
  const { eras } = useEraStore();
  const [selectedEra, setSelectedEra] = useState<number | null>(null);
  const [difficulty, setDifficulty] = useState<"beginner" | "intermediate" | "advanced">("beginner");
  const [questionCount, setQuestionCount] = useState<5 | 10>(5);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onStartQuiz(selectedEra, difficulty, questionCount);
  };

  return (
    <div className="max-w-2xl mx-auto">
      <div className="text-center mb-8">
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-primary-100 dark:bg-primary-900 mb-4">
          <Brain className="w-8 h-8 text-primary-700 dark:text-primary-300" />
        </div>
        <h2 className="font-heading text-2xl font-bold text-[hsl(var(--foreground))] mb-2">
          Start a New Quiz
        </h2>
        <p className="text-[hsl(var(--muted-foreground))]">
          Test your knowledge of church history
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Era Selection */}
        <div>
          <label htmlFor="era" className="block text-sm font-medium text-[hsl(var(--foreground))] mb-2">
            Select Era
          </label>
          <select
            id="era"
            value={selectedEra ?? ""}
            onChange={(e) => setSelectedEra(e.target.value ? Number(e.target.value) : null)}
            className={cn(
              "w-full rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))]",
              "px-4 py-2.5 text-[hsl(var(--foreground))]",
              "focus:outline-none focus:ring-2 focus:ring-[hsl(var(--ring))] focus:ring-offset-2"
            )}
          >
            <option value="">All Eras</option>
            {eras.map((era) => (
              <option key={era.id} value={era.id}>
                {era.name}
              </option>
            ))}
          </select>
        </div>

        {/* Difficulty Selection */}
        <div>
          <label className="block text-sm font-medium text-[hsl(var(--foreground))] mb-3">
            Difficulty Level
          </label>
          <div className="grid grid-cols-3 gap-3">
            {(["beginner", "intermediate", "advanced"] as const).map((level) => (
              <button
                key={level}
                type="button"
                onClick={() => setDifficulty(level)}
                className={cn(
                  "px-4 py-3 rounded-lg border-2 text-sm font-medium transition-colors",
                  "focus:outline-none focus:ring-2 focus:ring-[hsl(var(--ring))] focus:ring-offset-2",
                  difficulty === level
                    ? "border-primary-600 bg-primary-50 dark:bg-primary-950 text-primary-700 dark:text-primary-300"
                    : "border-[hsl(var(--border))] bg-[hsl(var(--card))] text-[hsl(var(--foreground))] hover:bg-[hsl(var(--muted))]"
                )}
              >
                {level.charAt(0).toUpperCase() + level.slice(1)}
              </button>
            ))}
          </div>
        </div>

        {/* Question Count */}
        <div>
          <label htmlFor="questionCount" className="block text-sm font-medium text-[hsl(var(--foreground))] mb-2">
            Number of Questions
          </label>
          <select
            id="questionCount"
            value={questionCount}
            onChange={(e) => setQuestionCount(Number(e.target.value) as 5 | 10)}
            className={cn(
              "w-full rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))]",
              "px-4 py-2.5 text-[hsl(var(--foreground))]",
              "focus:outline-none focus:ring-2 focus:ring-[hsl(var(--ring))] focus:ring-offset-2"
            )}
          >
            <option value={5}>5 Questions</option>
            <option value={10}>10 Questions</option>
          </select>
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={isLoading}
          className={cn(
            "w-full py-3 px-6 rounded-lg text-white font-medium",
            "bg-primary-600 hover:bg-primary-700 dark:bg-primary-700 dark:hover:bg-primary-600",
            "focus:outline-none focus:ring-2 focus:ring-[hsl(var(--ring))] focus:ring-offset-2",
            "transition-colors",
            isLoading && "opacity-50 cursor-not-allowed"
          )}
        >
          {isLoading ? "Generating Quiz..." : "Start Quiz"}
        </button>
      </form>
    </div>
  );
}
