import { useState } from "react";
import { cn } from "@/lib/utils";
import type { QuizQuestionItem } from "@/types";

type ShortAnswerQuestionProps = {
  question: QuizQuestionItem;
  onSubmit: (answer: string) => void;
  isSubmitted: boolean;
  isSubmitting: boolean;
};

export function ShortAnswerQuestion({ question, onSubmit, isSubmitted, isSubmitting }: ShortAnswerQuestionProps) {
  const [answer, setAnswer] = useState("");

  const handleSubmit = () => {
    if (answer.trim()) {
      onSubmit(answer.trim());
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium text-[hsl(var(--foreground))] mb-6">
          {question.questionText}
        </h3>

        <div>
          <textarea
            value={answer}
            onChange={(e) => !isSubmitted && setAnswer(e.target.value)}
            disabled={isSubmitted}
            placeholder="Type your answer here..."
            rows={4}
            className={cn(
              "w-full rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))]",
              "px-4 py-3 text-[hsl(var(--foreground))] placeholder:text-[hsl(var(--muted-foreground))]",
              "focus:outline-none focus:ring-2 focus:ring-[hsl(var(--ring))] focus:ring-offset-2",
              "resize-none",
              isSubmitted && "cursor-not-allowed opacity-75"
            )}
          />
          <p className="mt-2 text-xs text-[hsl(var(--muted-foreground))] text-right">
            {answer.length} characters
          </p>
        </div>
      </div>

      <button
        onClick={handleSubmit}
        disabled={!answer.trim() || isSubmitted || isSubmitting}
        className={cn(
          "w-full py-3 px-6 rounded-lg text-white font-medium",
          "bg-primary-600 hover:bg-primary-700 dark:bg-primary-700 dark:hover:bg-primary-600",
          "focus:outline-none focus:ring-2 focus:ring-[hsl(var(--ring))] focus:ring-offset-2",
          "transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        )}
      >
        {isSubmitting ? "Submitting..." : "Submit Answer"}
      </button>
    </div>
  );
}
