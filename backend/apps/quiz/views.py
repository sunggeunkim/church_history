"""API views for the quiz app.

Provides CRUD endpoints for quizzes and actions for submitting answers,
completing quizzes, and viewing quiz statistics.
"""

import logging

from django.db import transaction
from django.db.models import Avg, Count, F, FloatField
from django.db.models.functions import Cast
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Quiz, QuizQuestion
from .serializers import (
    QuizAnswerSerializer,
    QuizCreateSerializer,
    QuizListSerializer,
    QuizSerializer,
)
from .services import generate_quiz_questions, grade_short_answer
from .throttles import QuizBurstThrottle, QuizRateThrottle

logger = logging.getLogger(__name__)


class QuizViewSet(viewsets.ModelViewSet):
    """ViewSet for managing quizzes.

    Endpoints:
    - GET    /api/quiz/quizzes/                  - List user's quizzes
    - POST   /api/quiz/quizzes/                  - Create a new quiz
    - GET    /api/quiz/quizzes/{id}/             - Retrieve a quiz
    - POST   /api/quiz/quizzes/{id}/submit-answer/ - Submit an answer
    - POST   /api/quiz/quizzes/{id}/complete/    - Mark quiz as completed

    All endpoints require authentication and only return quizzes
    belonging to the authenticated user.
    """

    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post"]

    def get_throttles(self):
        """Apply rate limiting only to quiz creation."""
        if self.action == "create":
            return [QuizBurstThrottle(), QuizRateThrottle()]
        return []

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
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
        try:
            with transaction.atomic():
                quiz = serializer.save(user=self.request.user)
                generate_quiz_questions(quiz)
        except Exception as e:
            logger.exception("Failed to generate quiz questions: %s", e)
            raise ValidationError(
                {"detail": "Failed to generate quiz questions. Please try again."}
            )

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

        return Response(
            {
                "question_id": question.id,
                "is_correct": is_correct,
                "correct_answer": question.correct_answer,
                "explanation": question.explanation,
                "feedback": (
                    question.feedback
                    if question.question_type == QuizQuestion.QuestionType.SHORT_ANSWER
                    else None
                ),
            }
        )

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

        return Response(
            {
                "id": quiz.id,
                "score": quiz.score,
                "total_questions": quiz.total_questions,
                "percentage_score": quiz.percentage_score,
                "passed": quiz.passed,
                "completed_at": quiz.completed_at,
            }
        )


class QuizStatsView(GenericAPIView):
    """View for user quiz statistics.

    Endpoint:
    - GET /api/quiz/stats/

    Returns aggregate statistics for the authenticated user's quizzes.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get user's quiz statistics."""
        user = request.user

        # Get all completed quizzes for the user
        completed_quizzes = Quiz.objects.filter(
            user=user, completed_at__isnull=False
        ).select_related("era")

        total_quizzes = Quiz.objects.filter(user=user).count()
        total_completed = completed_quizzes.count()

        # Calculate average percentage score
        avg_score = (
            completed_quizzes.aggregate(
                avg=Avg(
                    Cast(F("score"), FloatField())
                    * 100.0
                    / Cast(F("total_questions"), FloatField())
                )
            )["avg"]
            or 0.0
        )

        # Count quizzes passed (>=70%)
        quizzes_passed = sum(1 for q in completed_quizzes if q.passed)

        # Calculate current streak (consecutive passed quizzes from most recent)
        current_streak = 0
        for quiz in completed_quizzes.order_by("-completed_at"):
            if quiz.passed:
                current_streak += 1
            else:
                break

        # Get stats by era
        by_era = []
        era_stats = (
            completed_quizzes.values("era__id", "era__name")
            .annotate(
                quizzes_completed=Count("id"),
                avg_score=Avg(
                    Cast(F("score"), FloatField())
                    * 100.0
                    / Cast(F("total_questions"), FloatField())
                ),
            )
            .order_by("era__id")
        )

        for stat in era_stats:
            by_era.append(
                {
                    "era_id": stat["era__id"],
                    "era_name": stat["era__name"] or "All Eras",
                    "quizzes_completed": stat["quizzes_completed"],
                    "average_score": round(stat["avg_score"] or 0, 1),
                }
            )

        return Response(
            {
                "total_quizzes": total_quizzes,
                "total_completed": total_completed,
                "average_score": round(avg_score, 1),
                "quizzes_passed": quizzes_passed,
                "current_streak": current_streak,
                "by_era": by_era,
            }
        )
