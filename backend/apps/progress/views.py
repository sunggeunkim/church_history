"""API views for the progress tracking app.

Provides endpoints for viewing progress summaries, marking eras as visited,
viewing achievements, and checking for newly unlocked achievements.
"""

import logging

from django.db.models import Avg, F, FloatField
from django.db.models.functions import Cast
from django.utils import timezone
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.chat.models import ChatSession
from apps.eras.models import Era
from apps.quiz.models import Quiz

from .models import Achievement, UserAchievement, UserProgress
from .serializers import MarkEraVisitedSerializer
from .services import calculate_activity_streak, check_and_unlock_achievements

logger = logging.getLogger(__name__)


class ProgressSummaryView(GenericAPIView):
    """Get user's overall progress summary.

    Endpoint: GET /api/progress/summary/
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Return comprehensive progress data."""
        user = request.user

        # Get all UserProgress for user
        user_progress = UserProgress.objects.filter(user=user).select_related("era")

        # Overall stats
        total_eras = Era.objects.count()
        eras_visited = user_progress.filter(era_visited=True).count()
        eras_chatted = user_progress.filter(chat_sessions_count__gt=0).count()
        eras_quizzed = user_progress.filter(quizzes_passed__gt=0).count()

        # Calculate overall completion
        total_activities = sum(
            p.completion_percentage / 100 * 3 for p in user_progress
        )
        max_activities = total_eras * 3
        completion_percentage = (
            round((total_activities / max_activities) * 100) if max_activities > 0 else 0
        )

        # Quiz stats
        completed_quizzes = Quiz.objects.filter(
            user=user, completed_at__isnull=False
        )
        total_quizzes = completed_quizzes.count()
        quizzes_passed = sum(1 for q in completed_quizzes if q.passed)

        avg_score = 0.0
        if total_quizzes > 0:
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

        # Streak and chat stats
        current_streak = calculate_activity_streak(user)
        total_chat_sessions = ChatSession.objects.filter(user=user).count()
        account_age_days = (timezone.now().date() - user.date_joined.date()).days

        # Per-era progress
        all_eras = Era.objects.all().order_by("order")
        progress_map = {p.era_id: p for p in user_progress}

        by_era = []
        for era in all_eras:
            p = progress_map.get(era.id)
            by_era.append(
                {
                    "era_id": era.id,
                    "era_name": era.name,
                    "era_slug": era.slug,
                    "era_color": era.color,
                    "era_visited": p.era_visited if p else False,
                    "first_visited_at": p.first_visited_at if p else None,
                    "chat_sessions_count": p.chat_sessions_count if p else 0,
                    "last_chat_at": p.last_chat_at if p else None,
                    "quizzes_completed": p.quizzes_completed if p else 0,
                    "quizzes_passed": p.quizzes_passed if p else 0,
                    "best_quiz_score": p.best_quiz_score if p else None,
                    "last_quiz_at": p.last_quiz_at if p else None,
                    "completion_percentage": p.completion_percentage if p else 0,
                }
            )

        # Recent activity (last 10 events)
        recent_activity = _build_recent_activity(user)

        return Response(
            {
                "overall": {
                    "completion_percentage": completion_percentage,
                    "eras_visited": eras_visited,
                    "eras_chatted": eras_chatted,
                    "eras_quizzed": eras_quizzed,
                    "total_eras": total_eras,
                },
                "stats": {
                    "total_quizzes": total_quizzes,
                    "quizzes_passed": quizzes_passed,
                    "average_score": round(avg_score, 1),
                    "current_streak": current_streak,
                    "total_chat_sessions": total_chat_sessions,
                    "account_age_days": account_age_days,
                },
                "by_era": by_era,
                "recent_activity": recent_activity,
            }
        )


class MarkEraVisitedView(GenericAPIView):
    """Mark an era as visited when user expands it on canvas.

    Endpoint: POST /api/progress/mark-era-visited/
    """

    permission_classes = [IsAuthenticated]
    serializer_class = MarkEraVisitedSerializer

    def post(self, request):
        """Mark era as visited (idempotent)."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        era_id = serializer.validated_data["era_id"]

        progress, _ = UserProgress.objects.get_or_create(
            user=request.user,
            era_id=era_id,
        )

        if not progress.era_visited:
            progress.era_visited = True
            progress.first_visited_at = timezone.now()
            progress.save(
                update_fields=["era_visited", "first_visited_at", "updated_at"]
            )

        return Response(
            {
                "era_id": era_id,
                "era_visited": progress.era_visited,
                "first_visited_at": progress.first_visited_at,
                "completion_percentage": progress.completion_percentage,
            }
        )


class AchievementListView(GenericAPIView):
    """List all achievements with user's unlock status.

    Endpoint: GET /api/progress/achievements/
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Return all achievements with unlock status."""
        user = request.user

        achievements = Achievement.objects.all()
        user_achievements = UserAchievement.objects.filter(user=user)
        unlocked_map = {ua.achievement_id: ua.unlocked_at for ua in user_achievements}

        achievement_data = []
        for achievement in achievements:
            achievement_data.append(
                {
                    "id": achievement.id,
                    "slug": achievement.slug,
                    "name": achievement.name,
                    "description": achievement.description,
                    "category": achievement.category,
                    "icon_key": achievement.icon_key,
                    "unlocked": achievement.id in unlocked_map,
                    "unlocked_at": unlocked_map.get(achievement.id),
                }
            )

        return Response(
            {
                "achievements": achievement_data,
                "total_unlocked": len(unlocked_map),
                "total_achievements": len(achievements),
            }
        )


class CheckAchievementsView(GenericAPIView):
    """Check and unlock newly earned achievements.

    Endpoint: POST /api/progress/check-achievements/
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Check and unlock any new achievements."""
        newly_unlocked = check_and_unlock_achievements(request.user)
        total_unlocked = UserAchievement.objects.filter(user=request.user).count()

        return Response(
            {
                "newly_unlocked": [
                    {
                        "id": ua.achievement.id,
                        "slug": ua.achievement.slug,
                        "name": ua.achievement.name,
                        "description": ua.achievement.description,
                        "category": ua.achievement.category,
                        "icon_key": ua.achievement.icon_key,
                        "unlocked_at": ua.unlocked_at,
                    }
                    for ua in newly_unlocked
                ],
                "total_unlocked": total_unlocked,
            }
        )


def _build_recent_activity(user, limit=10):
    """Build a list of recent activities from various sources."""
    activities = []

    # Recent era visits
    for p in (
        UserProgress.objects.filter(user=user, era_visited=True, first_visited_at__isnull=False)
        .select_related("era")
        .order_by("-first_visited_at")[:limit]
    ):
        activities.append(
            {
                "type": "visit",
                "era_name": p.era.name,
                "description": f"Explored {p.era.name} on canvas",
                "timestamp": p.first_visited_at.isoformat(),
            }
        )

    # Recent chat sessions
    for session in (
        ChatSession.objects.filter(user=user, era__isnull=False)
        .select_related("era")
        .order_by("-created_at")[:limit]
    ):
        activities.append(
            {
                "type": "chat",
                "era_name": session.era.name,
                "description": f"Started chat about {session.era.name}",
                "timestamp": session.created_at.isoformat(),
            }
        )

    # Recent completed quizzes
    for quiz in (
        Quiz.objects.filter(user=user, completed_at__isnull=False, era__isnull=False)
        .select_related("era")
        .order_by("-completed_at")[:limit]
    ):
        score_pct = round((quiz.score / quiz.total_questions) * 100) if quiz.total_questions > 0 else 0
        activities.append(
            {
                "type": "quiz",
                "era_name": quiz.era.name,
                "description": f"Completed quiz with {score_pct}%",
                "timestamp": quiz.completed_at.isoformat(),
            }
        )

    # Sort by timestamp descending and limit
    activities.sort(key=lambda a: a["timestamp"], reverse=True)
    return activities[:limit]
