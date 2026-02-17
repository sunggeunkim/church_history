import { motion } from "motion/react";
import { Check, X, ArrowRight } from "lucide-react";
import { cn } from "@/lib/utils";

type QuizFeedbackProps = {
  isCorrect: boolean;
  explanation: string;
  feedback?: string;
  onNext: () => void;
  isLastQuestion: boolean;
};

export function QuizFeedback({ isCorrect, explanation, feedback, onNext, isLastQuestion }: QuizFeedbackProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="space-y-6"
    >
      {/* Result Indicator */}
      <div className={cn(
        "rounded-lg p-6 border-2",
        isCorrect
          ? "border-green-200 bg-green-50 dark:border-green-900 dark:bg-green-950"
          : "border-red-200 bg-red-50 dark:border-red-900 dark:bg-red-950"
      )}>
        <div className="flex items-start gap-4">
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.1, type: "spring", stiffness: 200 }}
          >
            {isCorrect ? (
              <div className="flex-shrink-0 w-12 h-12 rounded-full bg-green-500 flex items-center justify-center">
                <Check className="w-6 h-6 text-white" />
              </div>
            ) : (
              <div className="flex-shrink-0 w-12 h-12 rounded-full bg-red-500 flex items-center justify-center">
                <X className="w-6 h-6 text-white" />
              </div>
            )}
          </motion.div>

          <div className="flex-1">
            <h3 className={cn(
              "text-xl font-bold mb-2",
              isCorrect ? "text-green-900 dark:text-green-100" : "text-red-900 dark:text-red-100"
            )}>
              {isCorrect ? "Correct!" : "Incorrect"}
            </h3>
            <p className={cn(
              "text-sm leading-relaxed",
              isCorrect ? "text-green-800 dark:text-green-200" : "text-red-800 dark:text-red-200"
            )}>
              {explanation}
            </p>
            {feedback && (
              <p className={cn(
                "mt-3 text-sm leading-relaxed pt-3 border-t",
                isCorrect
                  ? "border-green-200 dark:border-green-800 text-green-800 dark:text-green-200"
                  : "border-red-200 dark:border-red-800 text-red-800 dark:text-red-200"
              )}>
                {feedback}
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Next Button */}
      <button
        onClick={onNext}
        className={cn(
          "w-full py-3 px-6 rounded-lg text-white font-medium",
          "bg-primary-600 hover:bg-primary-700 dark:bg-primary-700 dark:hover:bg-primary-600",
          "focus:outline-none focus:ring-2 focus:ring-[hsl(var(--ring))] focus:ring-offset-2",
          "transition-colors flex items-center justify-center gap-2"
        )}
      >
        {isLastQuestion ? "See Results" : "Next Question"}
        <ArrowRight className="w-4 h-4" />
      </button>
    </motion.div>
  );
}
