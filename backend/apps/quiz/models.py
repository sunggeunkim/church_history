"""Quiz models for tests and quizzes.

Defines models for managing AI-generated quizzes, questions, and user answers
for the Toledot church history app.
"""

from django.conf import settings
from django.db import models


class Quiz(models.Model):
    """A quiz attempt by a user.

    Stores quiz metadata, score, and completion status. Questions are
    generated via OpenAI based on era content and difficulty level.
    """

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


class QuizQuestion(models.Model):
    """A single question within a quiz.

    Stores question text, type, options, correct answer, user answer,
    and AI-generated explanation/feedback.
    """

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
