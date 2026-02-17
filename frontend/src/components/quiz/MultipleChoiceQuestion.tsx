import { useState } from "react";
import { cn } from "@/lib/utils";
import type { QuizQuestionItem } from "@/types";

type MultipleChoiceQuestionProps = {
  question: QuizQuestionItem;
  onSubmit: (answer: string) => void;
  isSubmitted: boolean;
  isSubmitting: boolean;
};

export function MultipleChoiceQuestion({ question, onSubmit, isSubmitted, isSubmitting }: MultipleChoiceQuestionProps) {
  const [selectedOption, setSelectedOption] = useState<number | null>(null);

  const handleSubmit = () => {
    if (selectedOption !== null) {
      onSubmit(String(selectedOption));
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium text-[hsl(var(--foreground))] mb-6">
          {question.questionText}
        </h3>

        <div className="space-y-3">
          {question.options.map((option, index) => (
            <button
              key={index}
              onClick={() => !isSubmitted && setSelectedOption(index)}
              disabled={isSubmitted}
              className={cn(
                "w-full text-left px-4 py-3 rounded-lg border-2 transition-all",
                "focus:outline-none focus:ring-2 focus:ring-[hsl(var(--ring))] focus:ring-offset-2",
                selectedOption === index
                  ? "border-primary-600 bg-primary-50 dark:bg-primary-950"
                  : "border-[hsl(var(--border))] bg-[hsl(var(--card))]",
                !isSubmitted && "hover:border-primary-400",
                isSubmitted && "cursor-not-allowed opacity-75"
              )}
            >
              <div className="flex items-center gap-3">
                <div className={cn(
                  "flex-shrink-0 w-6 h-6 rounded-full border-2 flex items-center justify-center text-xs font-medium",
                  selectedOption === index
                    ? "border-primary-600 bg-primary-600 text-white"
                    : "border-[hsl(var(--border))] text-[hsl(var(--muted-foreground))]"
                )}>
                  {String.fromCharCode(65 + index)}
                </div>
                <span className="text-sm text-[hsl(var(--foreground))]">{option}</span>
              </div>
            </button>
          ))}
        </div>
      </div>

      <button
        onClick={handleSubmit}
        disabled={selectedOption === null || isSubmitted || isSubmitting}
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
