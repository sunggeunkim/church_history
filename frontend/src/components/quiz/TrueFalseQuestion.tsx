import { useState } from "react";
import { cn } from "@/lib/utils";
import { Check, X } from "lucide-react";
import type { QuizQuestionItem } from "@/types";

type TrueFalseQuestionProps = {
  question: QuizQuestionItem;
  onSubmit: (answer: string) => void;
  isSubmitted: boolean;
  isSubmitting: boolean;
};

export function TrueFalseQuestion({ question, onSubmit, isSubmitted, isSubmitting }: TrueFalseQuestionProps) {
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

        <div className="grid grid-cols-2 gap-4">
          <button
            onClick={() => !isSubmitted && setSelectedOption(0)}
            disabled={isSubmitted}
            className={cn(
              "px-6 py-8 rounded-lg border-2 transition-all",
              "focus:outline-none focus:ring-2 focus:ring-[hsl(var(--ring))] focus:ring-offset-2",
              selectedOption === 0
                ? "border-green-600 bg-green-50 dark:bg-green-950"
                : "border-[hsl(var(--border))] bg-[hsl(var(--card))]",
              !isSubmitted && "hover:border-green-400",
              isSubmitted && "cursor-not-allowed opacity-75"
            )}
          >
            <div className="flex flex-col items-center gap-2">
              <Check className={cn(
                "w-8 h-8",
                selectedOption === 0 ? "text-green-600" : "text-[hsl(var(--muted-foreground))]"
              )} />
              <span className={cn(
                "text-lg font-medium",
                selectedOption === 0 ? "text-green-700 dark:text-green-300" : "text-[hsl(var(--foreground))]"
              )}>
                True
              </span>
            </div>
          </button>

          <button
            onClick={() => !isSubmitted && setSelectedOption(1)}
            disabled={isSubmitted}
            className={cn(
              "px-6 py-8 rounded-lg border-2 transition-all",
              "focus:outline-none focus:ring-2 focus:ring-[hsl(var(--ring))] focus:ring-offset-2",
              selectedOption === 1
                ? "border-red-600 bg-red-50 dark:bg-red-950"
                : "border-[hsl(var(--border))] bg-[hsl(var(--card))]",
              !isSubmitted && "hover:border-red-400",
              isSubmitted && "cursor-not-allowed opacity-75"
            )}
          >
            <div className="flex flex-col items-center gap-2">
              <X className={cn(
                "w-8 h-8",
                selectedOption === 1 ? "text-red-600" : "text-[hsl(var(--muted-foreground))]"
              )} />
              <span className={cn(
                "text-lg font-medium",
                selectedOption === 1 ? "text-red-700 dark:text-red-300" : "text-[hsl(var(--foreground))]"
              )}>
                False
              </span>
            </div>
          </button>
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
