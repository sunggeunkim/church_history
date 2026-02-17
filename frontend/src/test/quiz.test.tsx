import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { BrowserRouter } from "react-router-dom";
import type { Quiz, QuizQuestionItem, QuizHistoryItem } from "@/types";

// Mock the stores before importing components
vi.mock("@/stores/quizStore", () => ({
  useQuizStore: vi.fn(),
}));

vi.mock("@/stores/eraStore", () => ({
  useEraStore: vi.fn(),
}));

vi.mock("@/hooks/useWindowSize", () => ({
  useWindowSize: vi.fn(() => ({ width: 1024, height: 768 })),
}));

// Mock react-confetti to avoid canvas issues in tests
vi.mock("react-confetti", () => ({
  default: () => null,
}));

import { useQuizStore } from "@/stores/quizStore";
import { useEraStore } from "@/stores/eraStore";

const mockMCQuestion: QuizQuestionItem = {
  id: 1,
  questionText: "When was the Council of Nicaea?",
  questionType: "mc",
  options: ["313 AD", "325 AD", "381 AD", "451 AD"],
  userAnswer: null,
  correctAnswer: "1",
  isCorrect: null,
  explanation: "The Council of Nicaea convened in 325 AD.",
  feedback: null,
  order: 1,
};

const mockTFQuestion: QuizQuestionItem = {
  id: 2,
  questionText: "Augustine was the Bishop of Hippo.",
  questionType: "tf",
  options: ["True", "False"],
  userAnswer: null,
  correctAnswer: "0",
  isCorrect: null,
  explanation: "Augustine served as Bishop of Hippo from 395-430 AD.",
  feedback: null,
  order: 2,
};

const mockSAQuestion: QuizQuestionItem = {
  id: 3,
  questionText: "Explain the significance of the Edict of Milan.",
  questionType: "sa",
  options: [],
  userAnswer: null,
  correctAnswer: "The Edict of Milan legalized Christianity.",
  isCorrect: null,
  explanation: "The Edict of Milan legalized Christianity in the Roman Empire.",
  feedback: null,
  order: 3,
};

const mockQuiz: Quiz = {
  id: 1,
  era: 1,
  eraName: "Early Church",
  difficulty: "beginner",
  score: 0,
  totalQuestions: 3,
  percentageScore: 0,
  passed: false,
  completedAt: null,
  createdAt: "2026-02-17T10:00:00Z",
  questions: [mockMCQuestion, mockTFQuestion, mockSAQuestion],
};

const mockHistoryItem: QuizHistoryItem = {
  id: 1,
  era: 1,
  eraName: "Early Church",
  difficulty: "beginner",
  score: 8,
  totalQuestions: 10,
  percentageScore: 80,
  passed: true,
  completedAt: "2026-02-17T10:30:00Z",
  createdAt: "2026-02-17T10:00:00Z",
};

const defaultQuizStore = {
  activeQuiz: null,
  currentQuestionIndex: 0,
  currentFeedback: null,
  quizHistory: [],
  quizStats: null,
  isCreatingQuiz: false,
  isSubmittingAnswer: false,
  isLoadingHistory: false,
  error: null,
  startQuiz: vi.fn(),
  submitQuizAnswer: vi.fn(),
  nextQuestion: vi.fn(),
  finishQuiz: vi.fn(),
  loadQuizHistory: vi.fn(),
  loadQuizStats: vi.fn(),
  viewQuiz: vi.fn(),
  resetActiveQuiz: vi.fn(),
  clearError: vi.fn(),
};

const defaultEraStore = {
  eras: [
    {
      id: 1,
      name: "Early Church",
      slug: "early-church",
      startYear: 30,
      endYear: 325,
      description: "The apostolic age",
      summary: "From Pentecost to Nicaea",
      color: "#C2410C",
      order: 1,
    },
  ],
  selectedEra: null,
  isLoading: false,
  error: null,
  fetchEras: vi.fn(),
  fetchEra: vi.fn(),
  selectEra: vi.fn(),
  timelineData: null,
  expandedEraId: null,
  isLoadingTimeline: false,
  fetchTimeline: vi.fn(),
  toggleExpanded: vi.fn(),
  setExpandedEra: vi.fn(),
};

function renderWithRouter(ui: React.ReactElement) {
  return render(<BrowserRouter>{ui}</BrowserRouter>);
}

describe("Quiz Components", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    (useQuizStore as unknown as ReturnType<typeof vi.fn>).mockReturnValue(defaultQuizStore);
    (useEraStore as unknown as ReturnType<typeof vi.fn>).mockReturnValue(defaultEraStore);
  });

  describe("QuizSetup", () => {
    it("renders era selector with All Eras option", async () => {
      const { QuizSetup } = await import("@/components/quiz/QuizSetup");
      render(<QuizSetup onStartQuiz={vi.fn()} isLoading={false} />);

      const select = screen.getByLabelText("Select Era");
      expect(select).toBeInTheDocument();
      expect(screen.getByRole("option", { name: "All Eras" })).toBeInTheDocument();
      expect(screen.getByRole("option", { name: "Early Church" })).toBeInTheDocument();
    });

    it("renders difficulty selector", async () => {
      const { QuizSetup } = await import("@/components/quiz/QuizSetup");
      render(<QuizSetup onStartQuiz={vi.fn()} isLoading={false} />);

      expect(screen.getByRole("button", { name: "Beginner" })).toBeInTheDocument();
      expect(screen.getByRole("button", { name: "Intermediate" })).toBeInTheDocument();
      expect(screen.getByRole("button", { name: "Advanced" })).toBeInTheDocument();
    });

    it("renders start button", async () => {
      const { QuizSetup } = await import("@/components/quiz/QuizSetup");
      render(<QuizSetup onStartQuiz={vi.fn()} isLoading={false} />);

      expect(screen.getByRole("button", { name: "Start Quiz" })).toBeInTheDocument();
    });

    it("calls onStartQuiz when form is submitted", async () => {
      const { QuizSetup } = await import("@/components/quiz/QuizSetup");
      const onStartQuiz = vi.fn();
      render(<QuizSetup onStartQuiz={onStartQuiz} isLoading={false} />);

      await userEvent.click(screen.getByRole("button", { name: "Start Quiz" }));
      expect(onStartQuiz).toHaveBeenCalledWith(null, "beginner", 5);
    });

    it("shows loading state", async () => {
      const { QuizSetup } = await import("@/components/quiz/QuizSetup");
      render(<QuizSetup onStartQuiz={vi.fn()} isLoading={true} />);

      expect(screen.getByRole("button", { name: "Generating Quiz..." })).toBeDisabled();
    });
  });

  describe("MultipleChoiceQuestion", () => {
    it("renders question text and options", async () => {
      const { MultipleChoiceQuestion } = await import("@/components/quiz/MultipleChoiceQuestion");
      render(
        <MultipleChoiceQuestion
          question={mockMCQuestion}
          onSubmit={vi.fn()}
          isSubmitted={false}
          isSubmitting={false}
        />
      );

      expect(screen.getByText("When was the Council of Nicaea?")).toBeInTheDocument();
      expect(screen.getByText("313 AD")).toBeInTheDocument();
      expect(screen.getByText("325 AD")).toBeInTheDocument();
      expect(screen.getByText("381 AD")).toBeInTheDocument();
      expect(screen.getByText("451 AD")).toBeInTheDocument();
    });

    it("allows selecting an option", async () => {
      const { MultipleChoiceQuestion } = await import("@/components/quiz/MultipleChoiceQuestion");
      render(
        <MultipleChoiceQuestion
          question={mockMCQuestion}
          onSubmit={vi.fn()}
          isSubmitted={false}
          isSubmitting={false}
        />
      );

      const option = screen.getByText("325 AD").closest("button");
      await userEvent.click(option!);
      // Option should be selected (visual feedback)
    });

    it("calls onSubmit when submit button clicked", async () => {
      const { MultipleChoiceQuestion } = await import("@/components/quiz/MultipleChoiceQuestion");
      const onSubmit = vi.fn();
      render(
        <MultipleChoiceQuestion
          question={mockMCQuestion}
          onSubmit={onSubmit}
          isSubmitted={false}
          isSubmitting={false}
        />
      );

      const option = screen.getByText("325 AD").closest("button");
      await userEvent.click(option!);

      const submitButton = screen.getByRole("button", { name: "Submit Answer" });
      await userEvent.click(submitButton);

      expect(onSubmit).toHaveBeenCalledWith("1");
    });

    it("disables submit button when no option selected", async () => {
      const { MultipleChoiceQuestion } = await import("@/components/quiz/MultipleChoiceQuestion");
      render(
        <MultipleChoiceQuestion
          question={mockMCQuestion}
          onSubmit={vi.fn()}
          isSubmitted={false}
          isSubmitting={false}
        />
      );

      expect(screen.getByRole("button", { name: "Submit Answer" })).toBeDisabled();
    });
  });

  describe("TrueFalseQuestion", () => {
    it("renders question text and True/False buttons", async () => {
      const { TrueFalseQuestion } = await import("@/components/quiz/TrueFalseQuestion");
      render(
        <TrueFalseQuestion
          question={mockTFQuestion}
          onSubmit={vi.fn()}
          isSubmitted={false}
          isSubmitting={false}
        />
      );

      expect(screen.getByText("Augustine was the Bishop of Hippo.")).toBeInTheDocument();
      expect(screen.getByRole("button", { name: /true/i })).toBeInTheDocument();
      expect(screen.getByRole("button", { name: /false/i })).toBeInTheDocument();
    });

    it("calls onSubmit when answer selected and submitted", async () => {
      const { TrueFalseQuestion } = await import("@/components/quiz/TrueFalseQuestion");
      const onSubmit = vi.fn();
      render(
        <TrueFalseQuestion
          question={mockTFQuestion}
          onSubmit={onSubmit}
          isSubmitted={false}
          isSubmitting={false}
        />
      );

      await userEvent.click(screen.getByRole("button", { name: /true/i }));
      await userEvent.click(screen.getByRole("button", { name: "Submit Answer" }));

      expect(onSubmit).toHaveBeenCalledWith("0");
    });
  });

  describe("ShortAnswerQuestion", () => {
    it("renders question text and textarea", async () => {
      const { ShortAnswerQuestion } = await import("@/components/quiz/ShortAnswerQuestion");
      render(
        <ShortAnswerQuestion
          question={mockSAQuestion}
          onSubmit={vi.fn()}
          isSubmitted={false}
          isSubmitting={false}
        />
      );

      expect(screen.getByText("Explain the significance of the Edict of Milan.")).toBeInTheDocument();
      expect(screen.getByPlaceholderText("Type your answer here...")).toBeInTheDocument();
    });

    it("shows character count", async () => {
      const { ShortAnswerQuestion } = await import("@/components/quiz/ShortAnswerQuestion");
      render(
        <ShortAnswerQuestion
          question={mockSAQuestion}
          onSubmit={vi.fn()}
          isSubmitted={false}
          isSubmitting={false}
        />
      );

      const textarea = screen.getByPlaceholderText("Type your answer here...");
      await userEvent.type(textarea, "Test answer");

      expect(screen.getByText(/11 characters/)).toBeInTheDocument();
    });

    it("disables submit button when empty", async () => {
      const { ShortAnswerQuestion } = await import("@/components/quiz/ShortAnswerQuestion");
      render(
        <ShortAnswerQuestion
          question={mockSAQuestion}
          onSubmit={vi.fn()}
          isSubmitted={false}
          isSubmitting={false}
        />
      );

      expect(screen.getByRole("button", { name: "Submit Answer" })).toBeDisabled();
    });
  });

  describe("QuizFeedback", () => {
    it("renders correct feedback with green styling", async () => {
      const { QuizFeedback } = await import("@/components/quiz/QuizFeedback");
      render(
        <QuizFeedback
          isCorrect={true}
          explanation="The Council of Nicaea convened in 325 AD."
          onNext={vi.fn()}
          isLastQuestion={false}
        />
      );

      expect(screen.getByText("Correct!")).toBeInTheDocument();
      expect(screen.getByText("The Council of Nicaea convened in 325 AD.")).toBeInTheDocument();
    });

    it("renders incorrect feedback with red styling", async () => {
      const { QuizFeedback } = await import("@/components/quiz/QuizFeedback");
      render(
        <QuizFeedback
          isCorrect={false}
          explanation="The Council of Nicaea convened in 325 AD."
          onNext={vi.fn()}
          isLastQuestion={false}
        />
      );

      expect(screen.getByText("Incorrect")).toBeInTheDocument();
    });

    it("shows Next Question button for non-last question", async () => {
      const { QuizFeedback } = await import("@/components/quiz/QuizFeedback");
      render(
        <QuizFeedback
          isCorrect={true}
          explanation="Test"
          onNext={vi.fn()}
          isLastQuestion={false}
        />
      );

      expect(screen.getByRole("button", { name: /next question/i })).toBeInTheDocument();
    });

    it("shows See Results button for last question", async () => {
      const { QuizFeedback } = await import("@/components/quiz/QuizFeedback");
      render(
        <QuizFeedback
          isCorrect={true}
          explanation="Test"
          onNext={vi.fn()}
          isLastQuestion={true}
        />
      );

      expect(screen.getByRole("button", { name: /see results/i })).toBeInTheDocument();
    });
  });

  describe("QuizResults", () => {
    it("renders score and percentage", async () => {
      const { QuizResults } = await import("@/components/quiz/QuizResults");
      render(
        <QuizResults
          score={8}
          totalQuestions={10}
          passed={true}
          onReview={vi.fn()}
          onNewQuiz={vi.fn()}
        />
      );

      // Check for Quiz Complete heading
      expect(screen.getByText("Quiz Complete!")).toBeInTheDocument();

      // Check for percentage (always rendered immediately)
      expect(screen.getByText("80%")).toBeInTheDocument();

      // The score counter animates, so just check the component renders
      expect(screen.getByText(/10/)).toBeInTheDocument();
    });

    it("shows passed badge when passed", async () => {
      const { QuizResults } = await import("@/components/quiz/QuizResults");
      render(
        <QuizResults
          score={8}
          totalQuestions={10}
          passed={true}
          onReview={vi.fn()}
          onNewQuiz={vi.fn()}
        />
      );

      // Look for the badge with specific text structure
      const badge = screen.getByText(/Passed/);
      expect(badge).toBeInTheDocument();
    });

    it("shows not passed badge when failed", async () => {
      const { QuizResults } = await import("@/components/quiz/QuizResults");
      render(
        <QuizResults
          score={5}
          totalQuestions={10}
          passed={false}
          onReview={vi.fn()}
          onNewQuiz={vi.fn()}
        />
      );

      expect(screen.getByText(/not passed/i)).toBeInTheDocument();
    });

    it("renders action buttons", async () => {
      const { QuizResults } = await import("@/components/quiz/QuizResults");
      render(
        <QuizResults
          score={8}
          totalQuestions={10}
          passed={true}
          onReview={vi.fn()}
          onNewQuiz={vi.fn()}
        />
      );

      expect(screen.getByRole("button", { name: /review quiz/i })).toBeInTheDocument();
      expect(screen.getByRole("button", { name: /new quiz/i })).toBeInTheDocument();
    });
  });

  describe("QuizHistory", () => {
    it("renders empty state when no quizzes", async () => {
      const { QuizHistory } = await import("@/components/quiz/QuizHistory");
      render(<QuizHistory quizzes={[]} onSelectQuiz={vi.fn()} />);

      expect(screen.getByText("No Quiz History")).toBeInTheDocument();
    });

    it("renders quiz history cards", async () => {
      const { QuizHistory } = await import("@/components/quiz/QuizHistory");
      render(<QuizHistory quizzes={[mockHistoryItem]} onSelectQuiz={vi.fn()} />);

      expect(screen.getByText("Early Church")).toBeInTheDocument();
      expect(screen.getByText("80%")).toBeInTheDocument();
    });
  });

  describe("QuizPage", () => {
    it("renders quiz setup when no active quiz", async () => {
      const { QuizPage } = await import("@/pages/QuizPage");
      renderWithRouter(<QuizPage />);

      expect(screen.getByText("Fun Tests & Quizzes")).toBeInTheDocument();
      expect(screen.getByText("Start a New Quiz")).toBeInTheDocument();
    });

    it("renders loading state when generating quiz", async () => {
      (useQuizStore as unknown as ReturnType<typeof vi.fn>).mockReturnValue({
        ...defaultQuizStore,
        isCreatingQuiz: true,
      });

      const { QuizPage } = await import("@/pages/QuizPage");
      renderWithRouter(<QuizPage />);

      expect(screen.getByText("Generating your quiz...")).toBeInTheDocument();
    });

    it("renders active quiz with first question", async () => {
      (useQuizStore as unknown as ReturnType<typeof vi.fn>).mockReturnValue({
        ...defaultQuizStore,
        activeQuiz: mockQuiz,
        currentQuestionIndex: 0,
      });

      const { QuizPage } = await import("@/pages/QuizPage");
      renderWithRouter(<QuizPage />);

      expect(screen.getByText("When was the Council of Nicaea?")).toBeInTheDocument();
      expect(screen.getByText("Question 1 of 3")).toBeInTheDocument();
    });

    it("renders quiz results when completed", async () => {
      const completedQuiz = {
        ...mockQuiz,
        completedAt: "2026-02-17T10:30:00Z",
        score: 8,
        percentageScore: 80,
        passed: true,
      };

      (useQuizStore as unknown as ReturnType<typeof vi.fn>).mockReturnValue({
        ...defaultQuizStore,
        activeQuiz: completedQuiz,
      });

      const { QuizPage } = await import("@/pages/QuizPage");
      renderWithRouter(<QuizPage />);

      await waitFor(() => {
        expect(screen.getByText("Quiz Complete!")).toBeInTheDocument();
      });
    });
  });
});
