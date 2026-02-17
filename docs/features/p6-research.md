# P6 Research: Fun Tests & Quizzes

**Research Date:** February 17, 2026
**Researcher:** AI Agent Team
**Purpose:** Technical research for the Toledot Fun Tests & Quizzes feature -- an AI-powered quiz system that generates and grades questions about church history, enabling users to test their knowledge and track their progress

---

## Table of Contents

1. [Feature Overview](#1-feature-overview)
2. [Existing Codebase Audit](#2-existing-codebase-audit)
3. [Architecture Decisions](#3-architecture-decisions)
4. [Backend: Data Model Design](#4-backend-data-model-design)
5. [Backend: API Endpoint Design](#5-backend-api-endpoint-design)
6. [Backend: OpenAI Integration](#6-backend-openai-integration)
7. [Frontend: Component Architecture](#7-frontend-component-architecture)
8. [Frontend: State Management](#8-frontend-state-management)
9. [Frontend: Quiz Flow UX](#9-frontend-quiz-flow-ux)
10. [Prompt Engineering](#10-prompt-engineering)
11. [Error Handling & Edge Cases](#11-error-handling--edge-cases)
12. [Performance Considerations](#12-performance-considerations)
13. [Licensing Summary](#13-licensing-summary)
14. [Architecture Decision Summary](#14-architecture-decision-summary)
15. [Implementation Checklist](#15-implementation-checklist)

---

## 1. Feature Overview

### What Are Fun Tests & Quizzes?

The Fun Tests & Quizzes feature is an AI-powered interactive assessment system that allows users to test their knowledge of church history. Unlike static quiz banks, this feature dynamically generates questions using OpenAI's API based on era content and user-selected difficulty.

### Core Features

1. **AI-Generated Questions**: Questions are generated on-demand based on:
   - Selected era (or "All Eras" for comprehensive quizzes)
   - Selected difficulty (Beginner, Intermediate, Advanced)
   - Era content (description, key events, key figures)

2. **Question Types**:
   - **Multiple Choice (MC)**: 4 options, single correct answer
   - **True/False (TF)**: Binary question
   - **Short Answer (SA)**: Open-ended text response, AI-graded

3. **Interactive Quiz Flow**:
   - User selects era and difficulty
   - System generates 5-10 questions via OpenAI
   - User answers each question sequentially
   - Immediate feedback after each answer (correct/incorrect + explanation)
   - Score summary at the end with animations
   - Option to review quiz after completion

4. **Quiz History**: Users can view their past quiz attempts with scores and filter by era.

### Why OpenAI Instead of Claude?

The app already uses Anthropic Claude (via the chat feature in P4). For quiz generation, we use **OpenAI GPT-4o** instead for the following reasons:

| Factor | OpenAI GPT-4o | Anthropic Claude |
|--------|--------------|-----------------|
| **JSON mode** | Native `response_format: "json_object"` with strict schema validation | Requires prompt engineering for JSON; no native JSON schema enforcement |
| **Cost per quiz** | ~$0.01 per quiz generation (5-10 questions) | ~$0.015 per quiz |
| **Latency** | Faster for batch generation (~2-3s for 10 questions) | Similar latency |
| **Short answer grading** | Excellent at structured evaluation tasks | Excellent, but no cost advantage |
| **API simplicity** | Single `chat.completions.create()` call with JSON mode | Requires XML tags or JSON prompt wrapping |

**Decision:** Use OpenAI GPT-4o for quiz generation and short-answer grading. This is a separate concern from the chat feature (which uses Claude for conversational RAG) and optimizes for structured data generation.

---

## 2. Existing Codebase Audit

### 2.1 Backend: Quiz App (Currently Empty)

The `backend/apps/quiz/` app exists but is a placeholder:

```python
# backend/apps/quiz/models.py (current state)
"""Quiz models for tests and quizzes.

Models will be implemented in P4 when quiz features are built.
"""
```

**Status:** The quiz app is registered in `INSTALLED_APPS` but has no models, views, or URLs. P6 will implement the full quiz system.

### 2.2 Backend: Era Data (Already Complete)

The `backend/apps/eras/models.py` provides:
- `Era`: name, slug, description, start_year, end_year, color
- `KeyEvent`: year, title, description (FK to Era)
- `KeyFigure`: name, birth/death years, title, description (FK to Era)

**All necessary data for quiz content generation is available.**

### 2.3 Backend: User Model

The `backend/apps/accounts/models.py` provides a custom User model extending `AbstractUser`. Quizzes will be associated with users via FK for history tracking.

### 2.4 Frontend: Quiz Page (Stub)

```tsx
// frontend/src/pages/QuizPage.tsx (current state)
export function QuizPage() {
  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto">
      <h1 className="text-3xl font-bold tracking-tight mb-4">Quizzes</h1>
      <div className="rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-6">
        <p className="text-[hsl(var(--muted-foreground))]">
          Quiz system will be implemented in P3.
        </p>
      </div>
    </div>
  );
}
```

**Status:** The page exists at `/quiz` route in `App.tsx` but is a placeholder. P6 will implement the full quiz UI.

### 2.5 Frontend: Existing Types

From `frontend/src/types/index.ts`:

```typescript
export type QuizQuestion = {
  id: string;
  question: string;
  options: string[];
  correctIndex: number;
  explanation: string;
};

export type ProgressSummary = {
  totalEras: number;
  completedEras: number;
  quizzesPassed: number;
  currentStreak: number;
  overallPercent: number;
};
```

**Note:** The existing `QuizQuestion` type is too simplistic for our needs (assumes only multiple choice). We'll extend it to support multiple question types.

### 2.6 Backend: OpenAI Integration (Not Yet Present)

The app currently uses:
- **Anthropic Claude** for chat (via `anthropic` Python SDK in `apps/chat/services.py`)
- **sentence-transformers** for embeddings (in `apps/content/views.py`)

**OpenAI is not yet integrated.** P6 will add the `openai` Python SDK for quiz generation.

### 2.7 Existing Patterns from Chat Feature

The chat feature provides useful patterns:
- **Async streaming**: `chat/views.py` uses async generators with SSE for streaming responses
- **Service layer**: `chat/services.py` separates business logic from views
- **Prompt engineering**: `SYSTEM_PROMPT` in `chat/services.py` shows how to structure AI prompts
- **Token tracking**: `ChatSession` tracks `total_input_tokens` and `total_output_tokens`
- **Error handling**: Graceful handling of API errors (RateLimitError, APIConnectionError, etc.)

**We'll apply similar patterns for the quiz feature.**

---

## 3. Architecture Decisions

### 3.1 AI Service Choice: OpenAI vs. Anthropic

**Decision: Use OpenAI GPT-4o for quiz generation and grading.**

Rationale:
1. **Native JSON mode**: OpenAI's `response_format: { type: "json_object" }` ensures valid JSON output, crucial for generating structured quiz questions
2. **Structured outputs**: OpenAI supports JSON schema validation via function calling, reducing prompt engineering complexity
3. **Cost efficiency**: Lower cost per quiz (~$0.01 vs. ~$0.015)
4. **Separation of concerns**: Chat uses Claude (conversational RAG), Quiz uses OpenAI (structured generation)

**Implementation:** Install `openai` Python SDK (MIT license) and create a separate `quiz/services.py` module for OpenAI interactions.

### 3.2 Quiz Generation: Real-Time vs. Pre-Generated

**Decision: Real-time generation on quiz start.**

| Approach | Pros | Cons |
|----------|------|------|
| **Real-time generation** | Fresh questions every time; adapts to current era data; no storage overhead | Requires API call on quiz start (~2-3s latency) |
| **Pre-generated bank** | Instant quiz start; no API costs per quiz | Requires seed script; questions become stale; less variety |

**Rationale for real-time:**
- AI generation is fast (~2-3s for 10 questions)
- Questions adapt to current era content (if we add more key events/figures later)
- No need for question bank management or duplicates
- Better user experience (unlimited unique quizzes)

**Trade-off:** Small latency on quiz start. We'll show a loading spinner with "Generating your quiz..." message.

### 3.3 Quiz State: Session-Based vs. Persistent

**Decision: Persistent quiz storage with full history.**

We store:
- `Quiz` model: user, era, difficulty, score, total_questions, completed_at, created_at
- `QuizQuestion` model: quiz FK, question_text, question_type, options (JSONField), correct_answer, user_answer, is_correct, explanation, order

**Why persistent storage?**
- Users can review past quizzes (learning tool)
- Progress tracking (quizzes completed, average score, streaks)
- Analytics (which eras are hardest, which question types users struggle with)
- Minimal storage cost (~500 bytes per question, ~5KB per quiz)

### 3.4 Question Order: Sequential vs. All-at-Once

**Decision: Sequential question flow (one at a time).**

| Approach | UX |
|----------|-----|
| **Sequential (one at a time)** | User sees one question, submits answer, gets immediate feedback, moves to next |
| **All-at-once (submit at end)** | User sees all questions on one screen, submits all answers, gets bulk feedback |

**Rationale for sequential:**
- Immediate feedback reinforces learning
- Less overwhelming (focused on one question at a time)
- Better for mobile UX (less scrolling)
- Aligns with quiz app conventions (Duolingo, Kahoot)

**Trade-off:** More clicking (10 "Next" buttons vs. 1 "Submit" button). We mitigate this with keyboard shortcuts (Enter to submit answer, Arrow keys to navigate).

### 3.5 Short Answer Grading: AI vs. Exact Match

**Decision: AI-powered grading using OpenAI.**

For short answer questions, exact string matching is insufficient (e.g., "Martin Luther nailed the 95 Theses to the church door" vs. "Luther posted his theses in Wittenberg").

**AI grading approach:**
1. After user submits short answer, send to OpenAI with:
   - The question
   - The correct answer (reference answer)
   - The user's answer
2. OpenAI evaluates and returns: `{ is_correct: boolean, feedback: string }`
3. Store result in `QuizQuestion.is_correct` and `QuizQuestion.feedback`

**Cost:** ~$0.002 per short answer grading. With 1-2 short answer questions per quiz, this is negligible.

### 3.6 Difficulty Levels: Implementation Strategy

**Decision: Difficulty affects question complexity, not just topic scope.**

| Difficulty | Question Characteristics | Example |
|-----------|-------------------------|---------|
| **Beginner** | Basic facts, key dates, major figures | "In what year did the Council of Nicaea convene?" |
| **Intermediate** | Conceptual understanding, cause-effect, significance | "Why was the Council of Nicaea significant for early church theology?" |
| **Advanced** | Analysis, comparison, nuance, theological debate | "Compare the Nicene and Chalcedonian formulations of Christology. How did the latter build upon the former?" |

**Implementation:** Pass difficulty as a prompt parameter to OpenAI. The AI adjusts question complexity based on difficulty level.

---

## 4. Backend: Data Model Design

### 4.1 Quiz Model

```python
# backend/apps/quiz/models.py

from django.conf import settings
from django.db import models


class Quiz(models.Model):
    """A quiz attempt by a user."""

    class Difficulty(models.TextChoices):
        BEGINNER = "beginner", "Beginner"
        INTERMEDIATE = "intermediate", "Intermediate"
        ADVANCED = "advanced", "Advanced"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="quizzes",
    )
    era = models.ForeignKey(
        "eras.Era",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="quizzes",
        help_text="Null for 'All Eras' quizzes",
    )
    difficulty = models.CharField(
        max_length=20,
        choices=Difficulty.choices,
        default=Difficulty.BEGINNER,
    )
    score = models.PositiveIntegerField(
        default=0,
        help_text="Number of correct answers",
    )
    total_questions = models.PositiveIntegerField(default=0)
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Null if quiz is in progress",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    # Token tracking for analytics
    generation_input_tokens = models.PositiveIntegerField(default=0)
    generation_output_tokens = models.PositiveIntegerField(default=0)
    grading_input_tokens = models.PositiveIntegerField(default=0)
    grading_output_tokens = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["user", "era"]),
        ]

    def __str__(self):
        era_name = self.era.name if self.era else "All Eras"
        return f"{self.user.email} - {era_name} ({self.difficulty}) - {self.score}/{self.total_questions}"

    @property
    def is_completed(self):
        """Check if the quiz has been completed."""
        return self.completed_at is not None

    @property
    def percentage_score(self):
        """Calculate the percentage score."""
        if self.total_questions == 0:
            return 0
        return round((self.score / self.total_questions) * 100)

    @property
    def passed(self):
        """Check if the user passed (70% or higher)."""
        return self.percentage_score >= 70
```

### 4.2 QuizQuestion Model

```python
class QuizQuestion(models.Model):
    """A single question within a quiz."""

    class QuestionType(models.TextChoices):
        MULTIPLE_CHOICE = "mc", "Multiple Choice"
        TRUE_FALSE = "tf", "True/False"
        SHORT_ANSWER = "sa", "Short Answer"

    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name="questions",
    )
    question_text = models.TextField()
    question_type = models.CharField(
        max_length=2,
        choices=QuestionType.choices,
    )
    options = models.JSONField(
        default=list,
        blank=True,
        help_text="Array of options for MC questions; ['True', 'False'] for TF; empty for SA",
    )
    correct_answer = models.TextField(
        help_text="Index (as string) for MC/TF, or reference answer text for SA",
    )
    user_answer = models.TextField(
        blank=True,
        help_text="Index (as string) for MC/TF, or user's text for SA",
    )
    is_correct = models.BooleanField(
        null=True,
        blank=True,
        help_text="Null if not yet answered",
    )
    explanation = models.TextField(
        blank=True,
        help_text="Explanation of the correct answer (AI-generated)",
    )
    feedback = models.TextField(
        blank=True,
        help_text="Personalized feedback for SA questions (AI-generated)",
    )
    order = models.PositiveIntegerField(
        help_text="Question order within the quiz",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["quiz", "order"]
        indexes = [
            models.Index(fields=["quiz", "order"]),
        ]

    def __str__(self):
        return f"Q{self.order}: {self.question_text[:50]}"
```

### 4.3 Model Design Rationale

| Field | Rationale |
|-------|-----------|
| `Quiz.era` (nullable FK) | Allows "All Eras" quizzes (era=null) vs. era-specific quizzes |
| `Quiz.completed_at` | Distinguishes in-progress quizzes from completed ones |
| `Quiz.score` | Denormalized for quick access (avoid COUNT query on every list) |
| `QuizQuestion.options` (JSONField) | Flexible storage for MC options; empty for TF/SA |
| `QuizQuestion.correct_answer` (TextField) | Stores index "0"-"3" for MC, "0"/"1" for TF, full text for SA |
| `QuizQuestion.user_answer` (TextField) | Same format as correct_answer for consistency |
| `QuizQuestion.is_correct` (nullable BooleanField) | Null until user submits answer; allows in-progress state |
| `QuizQuestion.feedback` | For SA questions, provides personalized AI feedback beyond generic explanation |
| Token tracking fields | Enables cost analytics and usage monitoring |

### 4.4 Database Migrations Plan

1. Create `Quiz` and `QuizQuestion` models
2. Add indexes for common queries (user quizzes, era-specific quizzes)
3. No seed data needed (quizzes are user-generated)

---

## 5. Backend: API Endpoint Design

### 5.1 Quiz Endpoints

All endpoints require authentication (`IsAuthenticated` permission).

#### POST /api/quiz/quizzes/

**Create a new quiz (generates questions via OpenAI).**

Request:
```json
{
  "era_id": 1,  // or null for "All Eras"
  "difficulty": "intermediate",
  "question_count": 10  // 5-10 questions
}
```

Response (201 Created):
```json
{
  "id": 42,
  "era": 1,
  "era_name": "Early Church",
  "difficulty": "intermediate",
  "score": 0,
  "total_questions": 10,
  "completed_at": null,
  "created_at": "2026-02-17T10:30:00Z",
  "questions": [
    {
      "id": 101,
      "question_text": "In what year did the Council of Nicaea convene?",
      "question_type": "mc",
      "options": ["313 AD", "325 AD", "381 AD", "451 AD"],
      "order": 1
      // No correct_answer or explanation sent until user submits
    },
    // ... 9 more questions
  ]
}
```

**Implementation:**
1. Validate request data (difficulty, era_id, question_count)
2. Fetch era content (description, key_events, key_figures)
3. Call OpenAI to generate questions (see section 6)
4. Create `Quiz` instance
5. Create `QuizQuestion` instances in bulk
6. Return serialized quiz with questions (without answers)

**Error handling:**
- 400 if invalid difficulty or question_count
- 404 if era_id not found
- 500 if OpenAI API fails (return friendly error message)

#### GET /api/quiz/quizzes/

**List user's quiz history.**

Query params:
- `era`: filter by era ID
- `completed`: filter by completion status (true/false)

Response (200 OK):
```json
{
  "count": 42,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 42,
      "era": 1,
      "era_name": "Early Church",
      "difficulty": "intermediate",
      "score": 8,
      "total_questions": 10,
      "percentage_score": 80,
      "passed": true,
      "completed_at": "2026-02-17T10:45:00Z",
      "created_at": "2026-02-17T10:30:00Z"
    },
    // ... more quizzes
  ]
}
```

#### GET /api/quiz/quizzes/{id}/

**Retrieve a specific quiz with all questions and answers.**

Response (200 OK):
```json
{
  "id": 42,
  "era": 1,
  "era_name": "Early Church",
  "difficulty": "intermediate",
  "score": 8,
  "total_questions": 10,
  "percentage_score": 80,
  "passed": true,
  "completed_at": "2026-02-17T10:45:00Z",
  "created_at": "2026-02-17T10:30:00Z",
  "questions": [
    {
      "id": 101,
      "question_text": "In what year did the Council of Nicaea convene?",
      "question_type": "mc",
      "options": ["313 AD", "325 AD", "381 AD", "451 AD"],
      "user_answer": "1",
      "correct_answer": "1",
      "is_correct": true,
      "explanation": "The Council of Nicaea was convened in 325 AD by Emperor Constantine...",
      "order": 1
    },
    // ... more questions with answers
  ]
}
```

**Permissions:** Only the quiz owner can retrieve their quiz.

#### POST /api/quiz/quizzes/{id}/submit-answer/

**Submit an answer to a specific question.**

Request:
```json
{
  "question_id": 101,
  "answer": "1"  // Index for MC/TF, or text for SA
}
```

Response (200 OK):
```json
{
  "question_id": 101,
  "is_correct": true,
  "correct_answer": "1",
  "explanation": "The Council of Nicaea was convened in 325 AD...",
  "feedback": null  // Only for SA questions
}
```

**Implementation:**
1. Validate question belongs to quiz and quiz belongs to user
2. Check if question already answered (idempotent: allow re-submission)
3. For MC/TF: compare user_answer to correct_answer
4. For SA: call OpenAI grading service (see section 6.3)
5. Update `QuizQuestion.user_answer`, `is_correct`, `feedback`
6. Return result

**Error handling:**
- 400 if answer format invalid
- 404 if question not found or doesn't belong to quiz
- 403 if quiz doesn't belong to user
- 500 if OpenAI grading fails (treat as incorrect with generic feedback)

#### POST /api/quiz/quizzes/{id}/complete/

**Mark quiz as completed.**

Request: (empty body)

Response (200 OK):
```json
{
  "id": 42,
  "score": 8,
  "total_questions": 10,
  "percentage_score": 80,
  "passed": true,
  "completed_at": "2026-02-17T10:45:00Z"
}
```

**Implementation:**
1. Calculate score (count is_correct=True questions)
2. Set `Quiz.score` and `Quiz.completed_at`
3. Return summary

**Error handling:**
- 404 if quiz not found or doesn't belong to user
- 400 if quiz already completed

#### GET /api/quiz/stats/

**Get user's quiz statistics.**

Response (200 OK):
```json
{
  "total_quizzes": 15,
  "total_completed": 12,
  "average_score": 78.5,
  "quizzes_passed": 10,
  "current_streak": 3,
  "by_era": [
    {
      "era_id": 1,
      "era_name": "Early Church",
      "quizzes_completed": 3,
      "average_score": 82.0
    },
    // ... more eras
  ]
}
```

**Implementation:** Aggregate queries on user's quizzes.

### 5.2 URL Configuration

```python
# backend/apps/quiz/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import QuizViewSet, QuizStatsView

app_name = "quiz"

router = DefaultRouter()
router.register(r"quizzes", QuizViewSet, basename="quiz")

urlpatterns = [
    path("", include(router.urls)),
    path("stats/", QuizStatsView.as_view(), name="stats"),
]
```

Include in main `urls.py`:
```python
path("api/quiz/", include("apps.quiz.urls")),
```

### 5.3 ViewSet Structure

```python
# backend/apps/quiz/views.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView

from .models import Quiz, QuizQuestion
from .serializers import (
    QuizSerializer,
    QuizListSerializer,
    QuizCreateSerializer,
    QuizAnswerSerializer,
)
from .services import generate_quiz_questions, grade_short_answer


class QuizViewSet(viewsets.ModelViewSet):
    """ViewSet for managing quizzes."""

    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post"]

    def get_serializer_class(self):
        if self.action == "create":
            return QuizCreateSerializer
        elif self.action == "list":
            return QuizListSerializer
        return QuizSerializer

    def get_queryset(self):
        """Return quizzes for the authenticated user."""
        queryset = Quiz.objects.filter(user=self.request.user).select_related("era")

        # Filter by era if specified
        era_id = self.request.query_params.get("era")
        if era_id:
            queryset = queryset.filter(era_id=era_id)

        # Filter by completion status
        completed = self.request.query_params.get("completed")
        if completed == "true":
            queryset = queryset.filter(completed_at__isnull=False)
        elif completed == "false":
            queryset = queryset.filter(completed_at__isnull=True)

        return queryset.prefetch_related("questions")

    def perform_create(self, serializer):
        """Create quiz and generate questions via OpenAI."""
        quiz = serializer.save(user=self.request.user)

        # Generate questions (this calls OpenAI)
        generate_quiz_questions(quiz)

    @action(detail=True, methods=["post"])
    def submit_answer(self, request, pk=None):
        """Submit an answer to a question."""
        quiz = self.get_object()

        serializer = QuizAnswerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        question_id = serializer.validated_data["question_id"]
        answer = serializer.validated_data["answer"]

        try:
            question = quiz.questions.get(id=question_id)
        except QuizQuestion.DoesNotExist:
            return Response(
                {"error": "Question not found in this quiz."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Grade the answer
        if question.question_type == QuizQuestion.QuestionType.SHORT_ANSWER:
            is_correct, feedback = grade_short_answer(
                question.question_text,
                question.correct_answer,
                answer,
            )
            question.feedback = feedback
        else:
            is_correct = answer == question.correct_answer

        question.user_answer = answer
        question.is_correct = is_correct
        question.save()

        return Response({
            "question_id": question.id,
            "is_correct": is_correct,
            "correct_answer": question.correct_answer,
            "explanation": question.explanation,
            "feedback": question.feedback if question.question_type == QuizQuestion.QuestionType.SHORT_ANSWER else None,
        })

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        """Mark quiz as completed and calculate score."""
        quiz = self.get_object()

        if quiz.completed_at:
            return Response(
                {"error": "Quiz already completed."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Calculate score
        quiz.score = quiz.questions.filter(is_correct=True).count()
        quiz.completed_at = timezone.now()
        quiz.save()

        return Response({
            "id": quiz.id,
            "score": quiz.score,
            "total_questions": quiz.total_questions,
            "percentage_score": quiz.percentage_score,
            "passed": quiz.passed,
            "completed_at": quiz.completed_at,
        })


class QuizStatsView(GenericAPIView):
    """View for user quiz statistics."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Implementation: aggregate user's quiz stats
        pass
```

---

## 6. Backend: OpenAI Integration

### 6.1 Python Package: openai SDK

**Package:** `openai`
**License:** MIT (Apache-2.0 license on GitHub)
**PyPI:** https://pypi.org/project/openai/
**Version:** Latest (1.x)
**Installation:** `pip install openai`

**Why this package?**
- Official OpenAI SDK for Python
- Supports all OpenAI models (GPT-4o, GPT-4, GPT-3.5)
- Native async support (`await client.chat.completions.create()`)
- JSON mode and structured outputs
- Active maintenance (weekly updates)

### 6.2 Quiz Generation Service

```python
# backend/apps/quiz/services.py

import json
import logging
from typing import List, Dict, Any

import openai
from django.conf import settings

from apps.eras.models import Era
from .models import Quiz, QuizQuestion

logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)


def generate_quiz_questions(quiz: Quiz) -> None:
    """Generate quiz questions using OpenAI GPT-4o.

    Creates QuizQuestion instances for the given quiz based on:
    - Quiz era (or all eras if era=null)
    - Quiz difficulty
    - Era content (description, key events, key figures)

    Args:
        quiz: The Quiz instance to generate questions for.

    Raises:
        openai.APIError: If OpenAI API call fails.
    """
    # Gather era content
    if quiz.era:
        era_context = _build_era_context(quiz.era)
        scope = f"the {quiz.era.name} era ({quiz.era.start_year}-{quiz.era.end_year or 'present'})"
    else:
        # "All Eras" quiz
        eras = Era.objects.all().prefetch_related("key_events", "key_figures")
        era_context = "\n\n".join([_build_era_context(era) for era in eras])
        scope = "all eras of church history"

    # Build prompt
    prompt = _build_generation_prompt(
        era_context=era_context,
        scope=scope,
        difficulty=quiz.difficulty,
        question_count=quiz.total_questions,
    )

    try:
        # Call OpenAI
        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,  # "gpt-4o"
            messages=[
                {
                    "role": "system",
                    "content": "You are a church history quiz generator. Generate questions in valid JSON format."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
            max_tokens=3000,
        )

        # Track tokens
        quiz.generation_input_tokens = response.usage.input_tokens
        quiz.generation_output_tokens = response.usage.output_tokens
        quiz.save(update_fields=["generation_input_tokens", "generation_output_tokens"])

        # Parse response
        questions_data = json.loads(response.choices[0].message.content)

        # Create QuizQuestion instances
        _create_quiz_questions(quiz, questions_data["questions"])

    except openai.APIError as e:
        logger.exception("OpenAI API error during quiz generation: %s", e)
        raise
    except json.JSONDecodeError as e:
        logger.exception("Failed to parse OpenAI JSON response: %s", e)
        raise
    except KeyError as e:
        logger.exception("Unexpected OpenAI response structure: %s", e)
        raise


def _build_era_context(era: Era) -> str:
    """Build context text for an era."""
    context_parts = [
        f"Era: {era.name} ({era.start_year}-{era.end_year or 'present'})",
        f"Description: {era.description}",
        "",
        "Key Events:",
    ]

    for event in era.key_events.all()[:10]:  # Limit to 10 events
        context_parts.append(f"- {event.year}: {event.title}")
        if event.description:
            context_parts.append(f"  {event.description[:200]}")

    context_parts.extend(["", "Key Figures:"])
    for figure in era.key_figures.all()[:10]:  # Limit to 10 figures
        years = ""
        if figure.birth_year and figure.death_year:
            years = f" ({figure.birth_year}-{figure.death_year})"
        context_parts.append(f"- {figure.name}{years}: {figure.title}")
        if figure.description:
            context_parts.append(f"  {figure.description[:200]}")

    return "\n".join(context_parts)


def _build_generation_prompt(
    era_context: str,
    scope: str,
    difficulty: str,
    question_count: int,
) -> str:
    """Build the prompt for quiz generation."""
    return f"""Generate a church history quiz with {question_count} questions about {scope}.

**Difficulty Level:** {difficulty}
- Beginner: Basic facts, key dates, major figures
- Intermediate: Conceptual understanding, cause-effect, significance
- Advanced: Analysis, comparison, theological nuance

**Question Type Distribution:**
- {question_count - 2} multiple choice questions (4 options each)
- 1 true/false question
- 1 short answer question

**Era Content:**
{era_context}

**Output Format (JSON):**
{{
  "questions": [
    {{
      "question_text": "What year was the Council of Nicaea?",
      "question_type": "mc",
      "options": ["313", "325", "381", "451"],
      "correct_answer": "1",
      "explanation": "The Council of Nicaea convened in 325 AD..."
    }},
    {{
      "question_text": "Augustine was the Bishop of Hippo.",
      "question_type": "tf",
      "options": ["True", "False"],
      "correct_answer": "0",
      "explanation": "Augustine served as Bishop of Hippo from 395-430 AD..."
    }},
    {{
      "question_text": "Explain the significance of the Edict of Milan.",
      "question_type": "sa",
      "options": [],
      "correct_answer": "The Edict of Milan (313 AD) legalized Christianity in the Roman Empire, ending persecution and marking a turning point...",
      "explanation": "A complete answer should mention: legalization of Christianity, end of persecution, Emperor Constantine, turning point for church growth."
    }}
  ]
}}

**Requirements:**
- Use historically accurate information from the era content provided
- Ensure all multiple choice questions have exactly 4 options
- For MC questions, correct_answer is the index (0-3) as a string
- For TF questions, correct_answer is "0" (True) or "1" (False)
- For SA questions, correct_answer is a reference answer (2-3 sentences)
- Each question must have a detailed explanation (2-3 sentences)
- Vary difficulty appropriately for the {difficulty} level
- Ensure questions are clear, unambiguous, and educational

Generate the quiz now in valid JSON format:"""


def _create_quiz_questions(quiz: Quiz, questions_data: List[Dict[str, Any]]) -> None:
    """Create QuizQuestion instances from parsed JSON."""
    question_instances = []

    for i, q_data in enumerate(questions_data):
        question_instances.append(
            QuizQuestion(
                quiz=quiz,
                question_text=q_data["question_text"],
                question_type=q_data["question_type"],
                options=q_data.get("options", []),
                correct_answer=q_data["correct_answer"],
                explanation=q_data["explanation"],
                order=i + 1,
            )
        )

    QuizQuestion.objects.bulk_create(question_instances)


def grade_short_answer(
    question_text: str,
    correct_answer: str,
    user_answer: str,
) -> tuple[bool, str]:
    """Grade a short answer question using OpenAI.

    Args:
        question_text: The question text.
        correct_answer: The reference answer.
        user_answer: The user's submitted answer.

    Returns:
        Tuple of (is_correct, feedback).
    """
    prompt = f"""Grade this short answer question:

**Question:** {question_text}

**Reference Answer:** {correct_answer}

**Student Answer:** {user_answer}

**Instructions:**
- Evaluate if the student's answer is correct (substantially matches the reference answer)
- Be lenient with wording differences
- Focus on key concepts, not exact phrasing
- Provide constructive feedback (1-2 sentences)

**Output Format (JSON):**
{{
  "is_correct": true,
  "feedback": "Excellent! You correctly identified the key significance of the Edict of Milan."
}}

or

{{
  "is_correct": false,
  "feedback": "Your answer misses the key point about legalization. The Edict of Milan legalized Christianity, ending persecution."
}}

Grade the answer now in valid JSON format:"""

    try:
        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are a church history teaching assistant grading student answers."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            response_format={"type": "json_object"},
            temperature=0.3,  # Lower temperature for consistent grading
            max_tokens=200,
        )

        result = json.loads(response.choices[0].message.content)
        return result["is_correct"], result["feedback"]

    except Exception as e:
        logger.exception("OpenAI API error during short answer grading: %s", e)
        # Fallback: mark as incorrect with generic feedback
        return False, "We couldn't grade your answer automatically. Please review the reference answer."
```

### 6.3 Settings Configuration

Add to `backend/config/settings.py`:

```python
# OpenAI Configuration
OPENAI_API_KEY = env("OPENAI_API_KEY")
OPENAI_MODEL = env("OPENAI_MODEL", default="gpt-4o")
```

Add to `.env`:
```
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-4o
```

---

## 7. Frontend: Component Architecture

### 7.1 New Components

```
src/
├── pages/
│   └── QuizPage.tsx                    # Enhanced: quiz selection and history
├── components/
│   └── quiz/                           # New: quiz-specific components
│       ├── QuizSetup.tsx                # Era and difficulty selection
│       ├── QuizQuestion.tsx             # Question display wrapper
│       ├── MultipleChoiceQuestion.tsx   # MC question UI
│       ├── TrueFalseQuestion.tsx        # TF question UI
│       ├── ShortAnswerQuestion.tsx      # SA question UI
│       ├── QuizProgress.tsx             # Progress bar (X of Y questions)
│       ├── QuizFeedback.tsx             # Immediate feedback after answer
│       ├── QuizResults.tsx              # Final score display with animations
│       ├── QuizHistory.tsx              # List of past quizzes
│       └── QuizHistoryCard.tsx          # Individual quiz history item
├── stores/
│   └── quizStore.ts                    # New: quiz state management
└── services/
    └── quizApi.ts                      # New: quiz API client
```

### 7.2 Component Tree

```
QuizPage
├── QuizSetup (if no active quiz)
│   ├── Era selector dropdown
│   ├── Difficulty selector (radio buttons)
│   ├── "Start Quiz" button
│   └── QuizHistory (collapsible)
│
└── QuizFlow (if active quiz)
    ├── QuizProgress
    │   └── "Question 3 of 10" + progress bar
    ├── QuizQuestion
    │   ├── MultipleChoiceQuestion
    │   │   ├── Question text
    │   │   ├── 4 option buttons
    │   │   └── "Submit Answer" button
    │   ├── TrueFalseQuestion
    │   │   ├── Question text
    │   │   ├── True/False buttons
    │   │   └── "Submit Answer" button
    │   └── ShortAnswerQuestion
    │       ├── Question text
    │       ├── Textarea input
    │       └── "Submit Answer" button
    ├── QuizFeedback (after submit)
    │   ├── Correct/Incorrect indicator (animated checkmark/X)
    │   ├── Explanation text
    │   ├── Feedback text (for SA)
    │   └── "Next Question" button
    └── QuizResults (after last question)
        ├── Score display (animated counter)
        ├── Percentage and pass/fail badge
        ├── Confetti animation (if passed)
        ├── "Review Quiz" button
        └── "Start New Quiz" button
```

### 7.3 Component Specifications

#### QuizSetup.tsx

Setup screen for starting a new quiz.

```tsx
type QuizSetupProps = {
  onStartQuiz: (eraId: number | null, difficulty: string, questionCount: number) => void;
};

export function QuizSetup({ onStartQuiz }: QuizSetupProps) {
  // Select era from dropdown (with "All Eras" option)
  // Select difficulty (Beginner/Intermediate/Advanced radio buttons)
  // Select question count (5/10 dropdown)
  // "Start Quiz" button calls onStartQuiz
  // Show QuizHistory below (collapsible)
}
```

#### QuizQuestion.tsx

Wrapper that renders the appropriate question type component.

```tsx
type QuizQuestionProps = {
  question: QuizQuestion;
  onSubmit: (answer: string) => void;
  isSubmitted: boolean;
  feedback: QuizFeedback | null;
};

export function QuizQuestion({ question, onSubmit, isSubmitted, feedback }: QuizQuestionProps) {
  // Switch on question.questionType
  // Render MultipleChoiceQuestion, TrueFalseQuestion, or ShortAnswerQuestion
  // Pass onSubmit callback
}
```

#### MultipleChoiceQuestion.tsx

Multiple choice question UI.

```tsx
type MultipleChoiceQuestionProps = {
  question: QuizQuestion;
  onSubmit: (answer: string) => void;
  isSubmitted: boolean;
};

export function MultipleChoiceQuestion({ question, onSubmit, isSubmitted }: MultipleChoiceQuestionProps) {
  // Render question text
  // Render 4 option buttons (radio style)
  // Track selected option
  // Disable after submission
  // "Submit Answer" button (disabled until option selected)
}
```

#### ShortAnswerQuestion.tsx

Short answer question UI.

```tsx
type ShortAnswerQuestionProps = {
  question: QuizQuestion;
  onSubmit: (answer: string) => void;
  isSubmitted: boolean;
};

export function ShortAnswerQuestion({ question, onSubmit, isSubmitted }: ShortAnswerQuestionProps) {
  // Render question text
  // Render textarea input (3-4 rows)
  // Track user input
  // "Submit Answer" button (disabled until input non-empty)
  // Disable textarea after submission
}
```

#### QuizFeedback.tsx

Feedback display after submitting an answer.

```tsx
type QuizFeedbackProps = {
  isCorrect: boolean;
  explanation: string;
  feedback?: string;  // For SA questions
  onNext: () => void;
};

export function QuizFeedback({ isCorrect, explanation, feedback, onNext }: QuizFeedbackProps) {
  // Animated checkmark (green) or X (red) icon
  // "Correct!" or "Incorrect" heading
  // Explanation text
  // Feedback text (if SA)
  // "Next Question" button (or "See Results" if last question)
}
```

#### QuizResults.tsx

Final score display with animations.

```tsx
type QuizResultsProps = {
  score: number;
  totalQuestions: number;
  passed: boolean;
  onReview: () => void;
  onNewQuiz: () => void;
};

export function QuizResults({ score, totalQuestions, passed, onReview, onNewQuiz }: QuizResultsProps) {
  // Animated score counter (0 -> score)
  // Percentage display
  // Pass/Fail badge with icon
  // Confetti animation (react-confetti) if passed
  // "Review Quiz" button
  // "Start New Quiz" button
}
```

#### QuizHistory.tsx

List of past quizzes.

```tsx
type QuizHistoryProps = {
  quizzes: QuizHistoryItem[];
  onSelectQuiz: (quizId: number) => void;
};

export function QuizHistory({ quizzes, onSelectQuiz }: QuizHistoryProps) {
  // Map quizzes to QuizHistoryCard components
  // Filter by era dropdown
  // Pagination if > 10 quizzes
}
```

#### QuizHistoryCard.tsx

Individual quiz history item.

```tsx
type QuizHistoryCardProps = {
  quiz: QuizHistoryItem;
  onClick: () => void;
};

export function QuizHistoryCard({ quiz, onClick }: QuizHistoryCardProps) {
  // Display era name, difficulty, score, date
  // Pass/Fail badge
  // Click to view details
}
```

---

## 8. Frontend: State Management

### 8.1 Quiz Store (Zustand)

```typescript
// frontend/src/stores/quizStore.ts

import { create } from "zustand";
import type { Quiz, QuizQuestion, QuizFeedback, QuizHistoryItem, QuizStats } from "@/types";
import {
  createQuiz,
  fetchQuiz,
  fetchQuizHistory,
  submitAnswer,
  completeQuiz,
  fetchQuizStats,
} from "@/services/quizApi";

type QuizState = {
  // Active quiz
  activeQuiz: Quiz | null;
  currentQuestionIndex: number;
  currentFeedback: QuizFeedback | null;

  // Quiz history
  quizHistory: QuizHistoryItem[];
  quizStats: QuizStats | null;

  // Loading states
  isCreatingQuiz: boolean;
  isSubmittingAnswer: boolean;
  isLoadingHistory: boolean;
  error: string | null;

  // Actions
  startQuiz: (eraId: number | null, difficulty: string, questionCount: number) => Promise<void>;
  submitQuizAnswer: (questionId: number, answer: string) => Promise<void>;
  nextQuestion: () => void;
  finishQuiz: () => Promise<void>;
  loadQuizHistory: () => Promise<void>;
  loadQuizStats: () => Promise<void>;
  viewQuiz: (quizId: number) => Promise<void>;
  resetActiveQuiz: () => void;
  clearError: () => void;
};

export const useQuizStore = create<QuizState>((set, get) => ({
  activeQuiz: null,
  currentQuestionIndex: 0,
  currentFeedback: null,
  quizHistory: [],
  quizStats: null,
  isCreatingQuiz: false,
  isSubmittingAnswer: false,
  isLoadingHistory: false,
  error: null,

  startQuiz: async (eraId, difficulty, questionCount) => {
    try {
      set({ isCreatingQuiz: true, error: null });
      const quiz = await createQuiz(eraId, difficulty, questionCount);
      set({
        activeQuiz: quiz,
        currentQuestionIndex: 0,
        currentFeedback: null,
        isCreatingQuiz: false,
      });
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : "Failed to create quiz",
        isCreatingQuiz: false,
      });
    }
  },

  submitQuizAnswer: async (questionId, answer) => {
    try {
      set({ isSubmittingAnswer: true, error: null });
      const feedback = await submitAnswer(
        get().activeQuiz!.id,
        questionId,
        answer
      );
      set({
        currentFeedback: feedback,
        isSubmittingAnswer: false,
      });
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : "Failed to submit answer",
        isSubmittingAnswer: false,
      });
    }
  },

  nextQuestion: () => {
    const { activeQuiz, currentQuestionIndex } = get();
    if (!activeQuiz) return;

    if (currentQuestionIndex < activeQuiz.questions.length - 1) {
      set({
        currentQuestionIndex: currentQuestionIndex + 1,
        currentFeedback: null,
      });
    } else {
      // Last question - trigger completion
      get().finishQuiz();
    }
  },

  finishQuiz: async () => {
    const { activeQuiz } = get();
    if (!activeQuiz) return;

    try {
      const result = await completeQuiz(activeQuiz.id);
      set((state) => ({
        activeQuiz: state.activeQuiz
          ? { ...state.activeQuiz, ...result }
          : null,
      }));
      // Reload history to include this quiz
      get().loadQuizHistory();
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : "Failed to complete quiz",
      });
    }
  },

  loadQuizHistory: async () => {
    try {
      set({ isLoadingHistory: true, error: null });
      const history = await fetchQuizHistory();
      set({ quizHistory: history, isLoadingHistory: false });
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : "Failed to load quiz history",
        isLoadingHistory: false,
      });
    }
  },

  loadQuizStats: async () => {
    try {
      const stats = await fetchQuizStats();
      set({ quizStats: stats });
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : "Failed to load quiz stats",
      });
    }
  },

  viewQuiz: async (quizId) => {
    try {
      const quiz = await fetchQuiz(quizId);
      set({
        activeQuiz: quiz,
        currentQuestionIndex: 0,
        currentFeedback: null,
      });
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : "Failed to load quiz",
      });
    }
  },

  resetActiveQuiz: () => {
    set({
      activeQuiz: null,
      currentQuestionIndex: 0,
      currentFeedback: null,
    });
  },

  clearError: () => {
    set({ error: null });
  },
}));
```

### 8.2 TypeScript Types

```typescript
// frontend/src/types/index.ts (additions)

export type Quiz = {
  id: number;
  era: number | null;
  eraName: string | null;
  difficulty: "beginner" | "intermediate" | "advanced";
  score: number;
  totalQuestions: number;
  percentageScore: number;
  passed: boolean;
  completedAt: string | null;
  createdAt: string;
  questions: QuizQuestion[];
};

export type QuizQuestion = {
  id: number;
  questionText: string;
  questionType: "mc" | "tf" | "sa";
  options: string[];
  userAnswer: string | null;
  correctAnswer: string | null;  // Null if not yet answered
  isCorrect: boolean | null;
  explanation: string;
  feedback: string | null;  // For SA questions
  order: number;
};

export type QuizFeedback = {
  questionId: number;
  isCorrect: boolean;
  correctAnswer: string;
  explanation: string;
  feedback?: string;  // For SA questions
};

export type QuizHistoryItem = {
  id: number;
  era: number | null;
  eraName: string | null;
  difficulty: string;
  score: number;
  totalQuestions: number;
  percentageScore: number;
  passed: boolean;
  completedAt: string;
  createdAt: string;
};

export type QuizStats = {
  totalQuizzes: number;
  totalCompleted: number;
  averageScore: number;
  quizzesPassed: number;
  currentStreak: number;
  byEra: {
    eraId: number;
    eraName: string;
    quizzesCompleted: number;
    averageScore: number;
  }[];
};
```

### 8.3 API Service Layer

```typescript
// frontend/src/services/quizApi.ts

import api from "./api";
import type { Quiz, QuizFeedback, QuizHistoryItem, QuizStats } from "@/types";

function mapQuiz(data: any): Quiz {
  return {
    id: data.id,
    era: data.era,
    eraName: data.era_name,
    difficulty: data.difficulty,
    score: data.score,
    totalQuestions: data.total_questions,
    percentageScore: data.percentage_score,
    passed: data.passed,
    completedAt: data.completed_at,
    createdAt: data.created_at,
    questions: data.questions.map((q: any) => ({
      id: q.id,
      questionText: q.question_text,
      questionType: q.question_type,
      options: q.options,
      userAnswer: q.user_answer,
      correctAnswer: q.correct_answer,
      isCorrect: q.is_correct,
      explanation: q.explanation,
      feedback: q.feedback,
      order: q.order,
    })),
  };
}

function mapQuizHistoryItem(data: any): QuizHistoryItem {
  return {
    id: data.id,
    era: data.era,
    eraName: data.era_name,
    difficulty: data.difficulty,
    score: data.score,
    totalQuestions: data.total_questions,
    percentageScore: data.percentage_score,
    passed: data.passed,
    completedAt: data.completed_at,
    createdAt: data.created_at,
  };
}

export async function createQuiz(
  eraId: number | null,
  difficulty: string,
  questionCount: number
): Promise<Quiz> {
  const response = await api.post("/quiz/quizzes/", {
    era_id: eraId,
    difficulty,
    question_count: questionCount,
  });
  return mapQuiz(response.data);
}

export async function fetchQuiz(quizId: number): Promise<Quiz> {
  const response = await api.get(`/quiz/quizzes/${quizId}/`);
  return mapQuiz(response.data);
}

export async function fetchQuizHistory(): Promise<QuizHistoryItem[]> {
  const response = await api.get("/quiz/quizzes/");
  return response.data.results.map(mapQuizHistoryItem);
}

export async function submitAnswer(
  quizId: number,
  questionId: number,
  answer: string
): Promise<QuizFeedback> {
  const response = await api.post(`/quiz/quizzes/${quizId}/submit_answer/`, {
    question_id: questionId,
    answer,
  });
  return {
    questionId: response.data.question_id,
    isCorrect: response.data.is_correct,
    correctAnswer: response.data.correct_answer,
    explanation: response.data.explanation,
    feedback: response.data.feedback,
  };
}

export async function completeQuiz(quizId: number): Promise<{
  score: number;
  totalQuestions: number;
  percentageScore: number;
  passed: boolean;
  completedAt: string;
}> {
  const response = await api.post(`/quiz/quizzes/${quizId}/complete/`);
  return {
    score: response.data.score,
    totalQuestions: response.data.total_questions,
    percentageScore: response.data.percentage_score,
    passed: response.data.passed,
    completedAt: response.data.completed_at,
  };
}

export async function fetchQuizStats(): Promise<QuizStats> {
  const response = await api.get("/quiz/stats/");
  return {
    totalQuizzes: response.data.total_quizzes,
    totalCompleted: response.data.total_completed,
    averageScore: response.data.average_score,
    quizzesPassed: response.data.quizzes_passed,
    currentStreak: response.data.current_streak,
    byEra: response.data.by_era.map((item: any) => ({
      eraId: item.era_id,
      eraName: item.era_name,
      quizzesCompleted: item.quizzes_completed,
      averageScore: item.average_score,
    })),
  };
}
```

---

## 9. Frontend: Quiz Flow UX

### 9.1 Quiz Flow State Machine

```
[Setup Screen]
    |
    | User clicks "Start Quiz"
    v
[Loading: Generating Quiz] (2-3s)
    |
    v
[Question 1] (unanswered)
    |
    | User selects answer and clicks "Submit"
    v
[Question 1 Feedback] (shows correct/incorrect + explanation)
    |
    | User clicks "Next Question"
    v
[Question 2] (unanswered)
    |
    | ...repeat for all questions...
    v
[Question 10 Feedback]
    |
    | User clicks "See Results"
    v
[Results Screen] (animated score display)
    |
    +-- User clicks "Review Quiz" -> [Review Mode: All Questions with Answers]
    +-- User clicks "Start New Quiz" -> [Setup Screen]
```

### 9.2 Keyboard Shortcuts

| Key | Action |
|-----|--------|
| **Enter** | Submit current answer (if answer selected/entered) |
| **1-4** | Select MC option 1-4 (if MC question) |
| **T/F** | Select True/False (if TF question) |
| **Ctrl+Enter** | Submit answer (alternative) |
| **→ (Right Arrow)** | Next question (after feedback shown) |
| **Escape** | Exit quiz (with confirmation) |

### 9.3 Animations

| Element | Animation | Library/Approach |
|---------|-----------|-----------------|
| Question transition | Slide in from right, slide out to left | Motion (framer-motion) |
| Feedback reveal | Fade in + slide down | Motion |
| Correct/Incorrect icon | Scale up + bounce | Motion + Lucide icons |
| Score counter | Count up from 0 to final score | Motion + useSpring |
| Confetti (if passed) | Confetti explosion | `react-confetti` (MIT) |
| Progress bar | Fill animation | CSS transition |

**New dependency:** `react-confetti` (MIT license)
- **Package:** `react-confetti`
- **npm:** https://www.npmjs.com/package/react-confetti
- **Weekly Downloads:** ~500k
- **License:** MIT
- **Bundle Size:** ~5KB gzipped

### 9.4 Loading States

| State | UI |
|-------|-----|
| **Quiz generation** | Full-screen spinner with "Generating your quiz..." text |
| **Answer submission** | Button spinner + disabled state |
| **Quiz history loading** | Skeleton cards |

### 9.5 Error States

| Error | UI |
|-------|-----|
| **Quiz generation failed** | Error alert with "Try Again" button |
| **Answer submission failed** | Toast notification + retry button |
| **Network error** | Offline indicator + cached state |

---

## 10. Prompt Engineering

### 10.1 Quiz Generation Prompt

See `_build_generation_prompt()` in section 6.2. Key elements:

1. **Era context**: Description, key events (with dates + descriptions), key figures (with years + titles)
2. **Difficulty level**: Clear guidance on question complexity for each level
3. **Question type distribution**: Specific counts for MC/TF/SA
4. **Output format**: Strict JSON schema with examples
5. **Requirements**: Accuracy, clarity, educational value

**Prompt engineering techniques:**
- **Few-shot examples**: Show 1 example per question type in the prompt
- **Explicit JSON schema**: Define exact structure with field names
- **Constraint specification**: "exactly 4 options", "correct_answer is index as string"
- **Domain grounding**: Provide era content to ensure historical accuracy

### 10.2 Short Answer Grading Prompt

See `grade_short_answer()` in section 6.3. Key elements:

1. **Question text**: Provide context
2. **Reference answer**: The "correct" answer to compare against
3. **Student answer**: The user's submitted text
4. **Grading criteria**: Focus on key concepts, not exact wording
5. **Output format**: JSON with `is_correct` boolean and `feedback` string

**Prompt engineering techniques:**
- **Rubric-based grading**: Explicit criteria ("Focus on key concepts, not exact phrasing")
- **Leniency instruction**: "Be lenient with wording differences"
- **Constructive feedback**: Request 1-2 sentence feedback, not just "wrong"
- **JSON mode**: Use `response_format: { type: "json_object" }` for structured output

### 10.3 Prompt Tuning Strategy

**Initial implementation:** Use the prompts in section 6.2 and 6.3.

**Iterative tuning:**
1. **Monitor quiz quality**: Collect feedback on question clarity, difficulty accuracy
2. **Analyze grading consistency**: Review SA grading feedback for false positives/negatives
3. **A/B test prompt variations**: Test different difficulty descriptions, constraint phrasings
4. **Adjust temperature**: 0.7 for generation (variety), 0.3 for grading (consistency)

**Edge cases to test:**
- **Beginner quiz with advanced era** (e.g., Beginner quiz on Medieval Scholasticism)
- **All Eras quiz** (ensure variety across eras, not clustering in one era)
- **Short answer grading edge cases** (partially correct, opposite answer, tangential answer)

---

## 11. Error Handling & Edge Cases

### 11.1 Backend Error Handling

| Error Scenario | Handling |
|----------------|----------|
| **OpenAI API rate limit** | Catch `openai.RateLimitError`, return 429 with retry-after header |
| **OpenAI API down** | Catch `openai.APIConnectionError`, return 503 Service Unavailable |
| **Malformed JSON from OpenAI** | Catch `json.JSONDecodeError`, log error, return 500 with friendly message |
| **Invalid era_id** | Return 404 Not Found |
| **Invalid difficulty** | Return 400 Bad Request with validation error |
| **Question count out of range** | Validate 5-10, return 400 if invalid |
| **User tries to answer another user's quiz** | Check quiz.user == request.user, return 403 Forbidden |
| **User tries to complete already-completed quiz** | Return 400 Bad Request |

### 11.2 Frontend Error Handling

| Error Scenario | Handling |
|----------------|----------|
| **Quiz generation timeout (>10s)** | Show timeout message, offer retry |
| **Network disconnection during quiz** | Cache quiz state locally, sync on reconnect |
| **Invalid answer format** | Client-side validation before submit |
| **Server returns 500** | Show friendly error, log to console, offer retry |

### 11.3 Edge Cases

| Edge Case | Handling |
|-----------|----------|
| **User refreshes page mid-quiz** | Zustand state is lost; show "Resume Quiz?" option using localStorage |
| **User starts multiple quizzes without finishing** | Allow multiple in-progress quizzes; show list in history with "Resume" button |
| **Era has no key events or figures** | OpenAI prompt gracefully handles empty context; generates questions from era description only |
| **All Eras quiz with 10 questions** | Distribute questions across eras (~1-2 per era) |
| **User submits empty short answer** | Client-side validation prevents submission |
| **OpenAI returns unexpected JSON structure** | Backend validates JSON schema, returns 500 if invalid |

---

## 12. Performance Considerations

### 12.1 Backend Performance

| Optimization | Implementation |
|-------------|----------------|
| **Database queries** | Use `select_related("era")` and `prefetch_related("questions")` to avoid N+1 |
| **OpenAI API caching** | No caching (questions should be fresh); but consider caching era context per-era |
| **Bulk question creation** | Use `QuizQuestion.objects.bulk_create()` for efficiency |
| **Quiz history pagination** | DRF pagination (25 per page) to avoid loading all quizzes |

### 12.2 Frontend Performance

| Optimization | Implementation |
|-------------|----------------|
| **Code splitting** | Lazy load QuizPage: `const QuizPage = lazy(() => import("./pages/QuizPage"))` |
| **Question preloading** | Load all questions on quiz start (already done in API response) |
| **Animation performance** | Use Motion's GPU-accelerated transforms (opacity, translate, scale) |
| **History loading** | Paginate quiz history, load 25 at a time |

### 12.3 API Cost Estimates

Assuming 1000 quizzes per month:

| Operation | Model | Tokens per call | Cost per call | Monthly cost (1000 quizzes) |
|-----------|-------|----------------|---------------|----------------------------|
| **Quiz generation (10 MC/TF questions)** | GPT-4o | ~1500 input, ~1200 output | ~$0.0075 | $7.50 |
| **Short answer grading (1 SA per quiz)** | GPT-4o | ~150 input, ~50 output | ~$0.001 | $1.00 |
| **Total** | | | | **~$8.50/month** |

**Note:** This is significantly cheaper than chat (which uses Claude Opus at ~$15/1M input tokens). Quiz generation is a cost-effective feature.

---

## 13. Licensing Summary

### New Backend Dependencies

| Package | License | PyPI | Purpose |
|---------|---------|------|---------|
| `openai` | MIT (Apache-2.0 on GitHub) | https://pypi.org/project/openai/ | OpenAI API client for quiz generation and grading |

### New Frontend Dependencies

| Package | License | npm | Purpose |
|---------|---------|-----|---------|
| `react-confetti` | MIT | https://www.npmjs.com/package/react-confetti | Confetti animation for quiz completion |

### Existing Dependencies (No Changes)

All existing dependencies (React, Tailwind, Zustand, Motion, DRF, Django, etc.) remain unchanged.

---

## 14. Architecture Decision Summary

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **AI service** | OpenAI GPT-4o | Native JSON mode, lower cost, structured outputs |
| **Quiz generation** | Real-time on quiz start | Fresh questions, adapts to data changes, better UX |
| **Quiz state** | Persistent storage | Enables history, progress tracking, review |
| **Question flow** | Sequential (one at a time) | Immediate feedback, less overwhelming, better for learning |
| **Short answer grading** | AI-powered (OpenAI) | Handles wording variations, provides feedback |
| **Difficulty implementation** | Prompt-based complexity | AI adjusts question complexity per difficulty level |
| **Animations** | Motion + react-confetti | Engaging UX, lightweight, performant |
| **Question types** | MC (4 options), TF, SA | Variety for engagement, tests different knowledge levels |
| **Question count** | 5-10 per quiz | Balances engagement with time commitment |
| **Passing score** | 70% | Standard educational threshold |

### Data Flow

```
User opens /quiz
    |
    v
QuizPage renders QuizSetup
    |
    | User selects era, difficulty, question count
    | User clicks "Start Quiz"
    v
quizStore.startQuiz(eraId, difficulty, questionCount)
    |
    v
POST /api/quiz/quizzes/
    |-- Backend fetches era content
    |-- Backend calls OpenAI to generate questions
    |-- Backend creates Quiz + QuizQuestion instances
    |-- Returns quiz with questions (no answers)
    |
    v
QuizPage renders QuizFlow with first question
    |
    | User answers question 1
    | User clicks "Submit Answer"
    v
quizStore.submitQuizAnswer(questionId, answer)
    |
    v
POST /api/quiz/quizzes/{id}/submit_answer/
    |-- Backend grades answer (instant for MC/TF, OpenAI for SA)
    |-- Backend updates QuizQuestion.user_answer, is_correct
    |-- Returns feedback
    |
    v
QuizFeedback displays result + explanation
    |
    | User clicks "Next Question"
    v
quizStore.nextQuestion() -> renders next question
    |
    | ...repeat for all questions...
    v
quizStore.finishQuiz()
    |
    v
POST /api/quiz/quizzes/{id}/complete/
    |-- Backend calculates score
    |-- Backend sets completed_at
    |-- Returns result summary
    |
    v
QuizResults displays animated score + confetti
    |
    +-- User clicks "Review Quiz" -> shows all questions with answers
    +-- User clicks "Start New Quiz" -> back to QuizSetup
```

---

## 15. Implementation Checklist

### Backend: Dependencies

- [ ] Install `openai` package: `pip install openai`
- [ ] Add `OPENAI_API_KEY` and `OPENAI_MODEL` to settings
- [ ] Add OpenAI API key to `.env` file

### Backend: Models

- [ ] Create `Quiz` model with fields: user, era, difficulty, score, total_questions, completed_at, token tracking
- [ ] Create `QuizQuestion` model with fields: quiz, question_text, question_type, options, correct_answer, user_answer, is_correct, explanation, feedback, order
- [ ] Add `@property` methods: `is_completed`, `percentage_score`, `passed`
- [ ] Create migrations and migrate database

### Backend: Services

- [ ] Create `apps/quiz/services.py`
- [ ] Implement `generate_quiz_questions(quiz)` function
- [ ] Implement `_build_era_context(era)` helper
- [ ] Implement `_build_generation_prompt()` helper
- [ ] Implement `_create_quiz_questions()` helper
- [ ] Implement `grade_short_answer()` function
- [ ] Add error handling for OpenAI API errors

### Backend: Views

- [ ] Create `QuizViewSet` with actions: list, retrieve, create
- [ ] Implement `create` action with `generate_quiz_questions()` call
- [ ] Implement `submit_answer` action with MC/TF/SA grading
- [ ] Implement `complete` action with score calculation
- [ ] Create `QuizStatsView` for user statistics
- [ ] Add permission checks (IsAuthenticated, quiz ownership)

### Backend: Serializers

- [ ] Create `QuizSerializer` (detail view with questions)
- [ ] Create `QuizListSerializer` (list view without questions)
- [ ] Create `QuizCreateSerializer` (create view)
- [ ] Create `QuizQuestionSerializer`
- [ ] Create `QuizAnswerSerializer` (for submit_answer action)

### Backend: URLs

- [ ] Create `apps/quiz/urls.py` with router
- [ ] Register `QuizViewSet` in router
- [ ] Add `/api/quiz/` to main `urls.py`

### Backend: Admin

- [ ] Register `Quiz` and `QuizQuestion` in admin
- [ ] Add list filters (era, difficulty, user, completed)
- [ ] Add search fields (user email, era name)

### Frontend: Dependencies

- [ ] Install `react-confetti`: `npm install react-confetti`

### Frontend: Types

- [ ] Add `Quiz`, `QuizQuestion`, `QuizFeedback`, `QuizHistoryItem`, `QuizStats` types to `src/types/index.ts`

### Frontend: API Service

- [ ] Create `src/services/quizApi.ts`
- [ ] Implement `createQuiz()`, `fetchQuiz()`, `fetchQuizHistory()`, `submitAnswer()`, `completeQuiz()`, `fetchQuizStats()`
- [ ] Add snake_case to camelCase mapping functions

### Frontend: State Management

- [ ] Create `src/stores/quizStore.ts`
- [ ] Implement `startQuiz()`, `submitQuizAnswer()`, `nextQuestion()`, `finishQuiz()`, `loadQuizHistory()`, `loadQuizStats()`, `viewQuiz()`, `resetActiveQuiz()` actions
- [ ] Add loading and error states

### Frontend: Components

- [ ] Create `src/components/quiz/QuizSetup.tsx` (era + difficulty selector)
- [ ] Create `src/components/quiz/QuizQuestion.tsx` (wrapper for question types)
- [ ] Create `src/components/quiz/MultipleChoiceQuestion.tsx`
- [ ] Create `src/components/quiz/TrueFalseQuestion.tsx`
- [ ] Create `src/components/quiz/ShortAnswerQuestion.tsx`
- [ ] Create `src/components/quiz/QuizProgress.tsx` (progress bar)
- [ ] Create `src/components/quiz/QuizFeedback.tsx` (correct/incorrect + explanation)
- [ ] Create `src/components/quiz/QuizResults.tsx` (score display + confetti)
- [ ] Create `src/components/quiz/QuizHistory.tsx` (list of past quizzes)
- [ ] Create `src/components/quiz/QuizHistoryCard.tsx`

### Frontend: Pages

- [ ] Enhance `src/pages/QuizPage.tsx` with quiz flow logic
- [ ] Implement QuizSetup / QuizFlow conditional rendering
- [ ] Add loading states (quiz generation spinner)
- [ ] Add error handling (toast notifications)

### Frontend: Animations

- [ ] Add Motion animations for question transitions
- [ ] Add Motion animations for feedback reveal
- [ ] Implement score counter animation
- [ ] Add confetti animation on quiz pass

### Frontend: UX Enhancements

- [ ] Implement keyboard shortcuts (Enter to submit, Arrow keys to navigate)
- [ ] Add progress bar with question count
- [ ] Add "Exit Quiz" confirmation dialog
- [ ] Add localStorage persistence for in-progress quiz (resume on refresh)

### Testing

- [ ] Unit test `generate_quiz_questions()` service
- [ ] Unit test `grade_short_answer()` service
- [ ] Unit test `QuizViewSet` endpoints (create, submit_answer, complete)
- [ ] Integration test: full quiz flow (create -> answer all -> complete)
- [ ] Frontend unit test: `quizStore` actions
- [ ] Frontend integration test: quiz flow (setup -> questions -> results)
- [ ] Manual test: all question types (MC, TF, SA)
- [ ] Manual test: all difficulty levels
- [ ] Manual test: All Eras quiz
- [ ] Manual test: keyboard shortcuts
- [ ] Manual test: error states (OpenAI API down, network error)

### Documentation

- [ ] Update API documentation with quiz endpoints
- [ ] Add quiz feature to user guide
- [ ] Document OpenAI prompt templates for future tuning

---

**End of Research Document**
**Prepared by:** AI Research Agent Team
**Date:** February 17, 2026
