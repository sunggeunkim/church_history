import { useEffect, useState } from "react";
import { motion } from "motion/react";
import Confetti from "react-confetti";
import { Trophy, RotateCcw, Eye } from "lucide-react";
import { cn } from "@/lib/utils";
import { useWindowSize } from "@/hooks/useWindowSize";
import { ShareButton } from "@/components/sharing/ShareButton";

type QuizResultsProps = {
  score: number;
  totalQuestions: number;
  passed: boolean;
  quizId?: number;
  onReview: () => void;
  onNewQuiz: () => void;
};

export function QuizResults({ score, totalQuestions, passed, quizId, onReview, onNewQuiz }: QuizResultsProps) {
  const [displayScore, setDisplayScore] = useState(0);
  const { width, height } = useWindowSize();
  const percentage = Math.round((score / totalQuestions) * 100);

  // Animate score counter
  useEffect(() => {
    let current = 0;
    const increment = score / 30;
    const timer = setInterval(() => {
      current += increment;
      if (current >= score) {
        setDisplayScore(score);
        clearInterval(timer);
      } else {
        setDisplayScore(Math.floor(current));
      }
    }, 50);
    return () => clearInterval(timer);
  }, [score]);

  return (
    <div className="max-w-2xl mx-auto">
      {/* Confetti */}
      {passed && <Confetti width={width} height={height} recycle={false} numberOfPieces={500} />}

      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5 }}
        className="text-center"
      >
        {/* Trophy Icon */}
        <div className={cn(
          "inline-flex items-center justify-center w-20 h-20 rounded-full mb-6",
          passed ? "bg-green-100 dark:bg-green-900" : "bg-orange-100 dark:bg-orange-900"
        )}>
          <Trophy className={cn(
            "w-10 h-10",
            passed ? "text-green-600 dark:text-green-400" : "text-orange-600 dark:text-orange-400"
          )} />
        </div>

        {/* Title */}
        <h2 className="font-heading text-3xl font-bold text-[hsl(var(--foreground))] mb-2">
          Quiz Complete!
        </h2>
        <p className="text-[hsl(var(--muted-foreground))] mb-8">
          {passed ? "Great job! You passed!" : "Keep practicing to improve!"}
        </p>

        {/* Score Display */}
        <div className="mb-8">
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.2, type: "spring", stiffness: 150 }}
            className="inline-block"
          >
            <div className="relative">
              {/* Circular Progress */}
              <svg className="w-48 h-48 transform -rotate-90">
                <circle
                  cx="96"
                  cy="96"
                  r="88"
                  stroke="hsl(var(--muted))"
                  strokeWidth="12"
                  fill="none"
                />
                <motion.circle
                  cx="96"
                  cy="96"
                  r="88"
                  stroke={passed ? "rgb(34, 197, 94)" : "rgb(249, 115, 22)"}
                  strokeWidth="12"
                  fill="none"
                  strokeLinecap="round"
                  initial={{ strokeDasharray: "0 552" }}
                  animate={{ strokeDasharray: `${(percentage / 100) * 552} 552` }}
                  transition={{ duration: 1.5, ease: "easeOut" }}
                />
              </svg>
              {/* Score Text */}
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <div className="text-5xl font-bold text-[hsl(var(--foreground))]">
                  {displayScore}/{totalQuestions}
                </div>
                <div className={cn(
                  "text-2xl font-semibold mt-1",
                  passed ? "text-green-600 dark:text-green-400" : "text-orange-600 dark:text-orange-400"
                )}>
                  {percentage}%
                </div>
              </div>
            </div>
          </motion.div>
        </div>

        {/* Pass/Fail Badge */}
        <div className="mb-8">
          <span className={cn(
            "inline-block px-6 py-2 rounded-full text-sm font-semibold",
            passed
              ? "bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200"
              : "bg-orange-100 dark:bg-orange-900 text-orange-800 dark:text-orange-200"
          )}>
            {passed ? "Passed" : "Not Passed"} (70% required)
          </span>
        </div>

        {/* Action Buttons */}
        <div className="grid grid-cols-2 gap-4">
          <button
            onClick={onReview}
            className={cn(
              "py-3 px-6 rounded-lg font-medium border-2",
              "border-[hsl(var(--border))] bg-[hsl(var(--card))] text-[hsl(var(--foreground))]",
              "hover:bg-[hsl(var(--muted))]",
              "focus:outline-none focus:ring-2 focus:ring-[hsl(var(--ring))] focus:ring-offset-2",
              "transition-colors flex items-center justify-center gap-2"
            )}
          >
            <Eye className="w-4 h-4" />
            Review Quiz
          </button>
          <button
            onClick={onNewQuiz}
            className={cn(
              "py-3 px-6 rounded-lg text-white font-medium",
              "bg-primary-600 hover:bg-primary-700 dark:bg-primary-700 dark:hover:bg-primary-600",
              "focus:outline-none focus:ring-2 focus:ring-[hsl(var(--ring))] focus:ring-offset-2",
              "transition-colors flex items-center justify-center gap-2"
            )}
          >
            <RotateCcw className="w-4 h-4" />
            New Quiz
          </button>
        </div>

        {/* Share Quiz Result */}
        {quizId !== undefined && (
          <div className="mt-4 flex justify-center">
            <ShareButton
              shareType="quiz_result"
              quizId={quizId}
              variant="button"
              label="Share Result"
            />
          </div>
        )}
      </motion.div>
    </div>
  );
}
