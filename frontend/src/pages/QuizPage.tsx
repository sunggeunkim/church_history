import { useEffect } from "react";
import { Loader2 } from "lucide-react";
import { useQuizStore } from "@/stores/quizStore";
import { useEraStore } from "@/stores/eraStore";
import { QuizSetup } from "@/components/quiz/QuizSetup";
import { QuizProgress } from "@/components/quiz/QuizProgress";
import { MultipleChoiceQuestion } from "@/components/quiz/MultipleChoiceQuestion";
import { TrueFalseQuestion } from "@/components/quiz/TrueFalseQuestion";
import { ShortAnswerQuestion } from "@/components/quiz/ShortAnswerQuestion";
import { QuizFeedback } from "@/components/quiz/QuizFeedback";
import { QuizResults } from "@/components/quiz/QuizResults";
import { QuizHistory } from "@/components/quiz/QuizHistory";

export function QuizPage() {
  const {
    activeQuiz,
    currentQuestionIndex,
    currentFeedback,
    quizHistory,
    isCreatingQuiz,
    isSubmittingAnswer,
    isLoadingHistory,
    error,
    startQuiz,
    submitQuizAnswer,
    nextQuestion,
    loadQuizHistory,
    viewQuiz,
    resetActiveQuiz,
    clearError,
  } = useQuizStore();

  const { eras, fetchEras } = useEraStore();

  useEffect(() => {
    fetchEras();
    loadQuizHistory();
  }, [fetchEras, loadQuizHistory]);

  const handleStartQuiz = async (eraId: number | null, difficulty: string, questionCount: number) => {
    await startQuiz(eraId, difficulty, questionCount);
  };

  const handleSubmitAnswer = async (answer: string) => {
    const currentQuestion = activeQuiz?.questions[currentQuestionIndex];
    if (currentQuestion) {
      await submitQuizAnswer(currentQuestion.id, answer);
    }
  };

  const handleReviewQuiz = () => {
    // Quiz is already loaded - just reset to first question for review
    // In review mode, questions will show answers
  };

  const handleNewQuiz = () => {
    resetActiveQuiz();
    clearError();
  };

  const handleViewHistory = async (quizId: number) => {
    await viewQuiz(quizId);
  };

  // Loading state while generating quiz
  if (isCreatingQuiz) {
    return (
      <div className="flex h-full items-center justify-center p-4">
        <div className="text-center">
          <Loader2 className="mx-auto h-12 w-12 animate-spin text-primary-600 dark:text-primary-400 mb-4" />
          <h2 className="font-heading text-xl font-semibold text-[hsl(var(--foreground))] mb-2">
            Generating your quiz...
          </h2>
          <p className="text-sm text-[hsl(var(--muted-foreground))]">
            This will only take a moment
          </p>
        </div>
      </div>
    );
  }

  // Error state
  if (error && !activeQuiz) {
    return (
      <div className="p-4 sm:p-6 lg:p-8 max-w-4xl mx-auto">
        <div className="rounded-lg border border-red-200 bg-red-50 dark:border-red-900 dark:bg-red-950 p-6">
          <h3 className="font-medium text-red-800 dark:text-red-200 mb-2">
            Failed to load quiz
          </h3>
          <p className="text-sm text-red-700 dark:text-red-300 mb-4">{error}</p>
          <button
            onClick={() => {
              clearError();
              resetActiveQuiz();
            }}
            className="px-4 py-2 rounded-lg bg-red-600 text-white text-sm font-medium hover:bg-red-700 transition-colors"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  // Quiz completed - show results
  if (activeQuiz && activeQuiz.completedAt) {
    return (
      <div className="p-4 sm:p-6 lg:p-8 max-w-4xl mx-auto">
        <QuizResults
          score={activeQuiz.score}
          totalQuestions={activeQuiz.totalQuestions}
          passed={activeQuiz.passed}
          quizId={activeQuiz.id}
          onReview={handleReviewQuiz}
          onNewQuiz={handleNewQuiz}
        />
      </div>
    );
  }

  // Active quiz in progress
  if (activeQuiz && !activeQuiz.completedAt) {
    const currentQuestion = activeQuiz.questions[currentQuestionIndex];

    return (
      <div className="p-4 sm:p-6 lg:p-8 max-w-3xl mx-auto">
        <div className="space-y-6">
          {/* Progress Bar */}
          <QuizProgress
            currentQuestion={currentQuestionIndex}
            totalQuestions={activeQuiz.totalQuestions}
            eraName={activeQuiz.eraName}
            difficulty={activeQuiz.difficulty}
          />

          {/* Question Card */}
          <div className="rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-6">
            {currentFeedback ? (
              // Show feedback after answer submitted
              <QuizFeedback
                isCorrect={currentFeedback.isCorrect}
                explanation={currentFeedback.explanation}
                feedback={currentFeedback.feedback ?? undefined}
                onNext={nextQuestion}
                isLastQuestion={currentQuestionIndex === activeQuiz.questions.length - 1}
              />
            ) : (
              // Show question
              <>
                {currentQuestion.questionType === "mc" && (
                  <MultipleChoiceQuestion
                    question={currentQuestion}
                    onSubmit={handleSubmitAnswer}
                    isSubmitted={false}
                    isSubmitting={isSubmittingAnswer}
                  />
                )}
                {currentQuestion.questionType === "tf" && (
                  <TrueFalseQuestion
                    question={currentQuestion}
                    onSubmit={handleSubmitAnswer}
                    isSubmitted={false}
                    isSubmitting={isSubmittingAnswer}
                  />
                )}
                {currentQuestion.questionType === "sa" && (
                  <ShortAnswerQuestion
                    question={currentQuestion}
                    onSubmit={handleSubmitAnswer}
                    isSubmitted={false}
                    isSubmitting={isSubmittingAnswer}
                  />
                )}
              </>
            )}
          </div>
        </div>
      </div>
    );
  }

  // Default: show quiz setup and history
  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-6xl mx-auto">
      <div className="mb-8">
        <h1 className="font-heading text-3xl font-bold tracking-tight text-[hsl(var(--foreground))] mb-2">
          Fun Tests & Quizzes
        </h1>
        <p className="text-[hsl(var(--muted-foreground))]">
          Test your knowledge of church history with AI-generated quizzes
        </p>
      </div>

      <div className="grid lg:grid-cols-2 gap-8">
        {/* Quiz Setup */}
        <div>
          <QuizSetup onStartQuiz={handleStartQuiz} isLoading={isCreatingQuiz} />
        </div>

        {/* Quiz History */}
        <div>
          {isLoadingHistory ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-[hsl(var(--muted-foreground))]" />
            </div>
          ) : (
            <QuizHistory quizzes={quizHistory} onSelectQuiz={handleViewHistory} />
          )}
        </div>
      </div>
    </div>
  );
}
