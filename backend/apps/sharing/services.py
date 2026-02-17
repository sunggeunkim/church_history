"""Service functions for building share content snapshots."""

from django.db.models import Avg, F, FloatField
from django.db.models.functions import Cast
from django.shortcuts import get_object_or_404

from apps.progress.models import Achievement, UserAchievement, UserProgress
from apps.quiz.models import Quiz


def build_content_snapshot(user, share_type, achievement_id=None, quiz_id=None):
    """Build a content snapshot dict for the given share type.

    Args:
        user: The authenticated user creating the share link.
        share_type: One of "achievement", "quiz_result", "progress".
        achievement_id: Required if share_type is "achievement".
        quiz_id: Required if share_type is "quiz_result".

    Returns:
        A dict containing the snapshot data.

    Raises:
        Http404: If the referenced content is not found or not owned by user.
    """
    if share_type == "achievement":
        return _build_achievement_snapshot(user, achievement_id)
    elif share_type == "quiz_result":
        return _build_quiz_snapshot(user, quiz_id)
    elif share_type == "progress":
        return _build_progress_snapshot(user)
    else:
        raise ValueError(f"Unknown share_type: {share_type}")


def _build_achievement_snapshot(user, achievement_id):
    """Build snapshot for an unlocked achievement."""
    user_achievement = get_object_or_404(
        UserAchievement.objects.select_related("achievement"),
        user=user,
        achievement_id=achievement_id,
    )
    achievement = user_achievement.achievement
    return {
        "achievement_slug": achievement.slug,
        "achievement_name": achievement.name,
        "achievement_description": achievement.description,
        "achievement_category": achievement.category,
        "achievement_icon_key": achievement.icon_key,
        "unlocked_at": user_achievement.unlocked_at.strftime("%B %-d, %Y"),
    }


def _build_quiz_snapshot(user, quiz_id):
    """Build snapshot for a completed quiz."""
    quiz = get_object_or_404(
        Quiz,
        id=quiz_id,
        user=user,
        completed_at__isnull=False,
    )
    return {
        "quiz_id": quiz.id,
        "era_name": quiz.era.name if quiz.era else "All Eras",
        "difficulty": quiz.difficulty,
        "score": quiz.score,
        "total_questions": quiz.total_questions,
        "percentage_score": quiz.percentage_score,
        "passed": quiz.passed,
        "completed_at": quiz.completed_at.isoformat(),
    }


def _build_progress_snapshot(user):
    """Build snapshot for the user's current progress summary."""
    from apps.chat.models import ChatSession
    from apps.eras.models import Era
    from apps.progress.services import calculate_activity_streak

    user_progress = UserProgress.objects.filter(user=user)
    total_eras = Era.objects.count()

    # Achievement stats
    achievements_unlocked = UserAchievement.objects.filter(user=user).count()
    total_achievements = Achievement.objects.count()

    # Quiz stats (DB-level aggregation)
    completed_quizzes = Quiz.objects.filter(
        user=user, completed_at__isnull=False
    )
    total_quizzes = completed_quizzes.count()

    quizzes_passed = completed_quizzes.filter(total_questions__gt=0).annotate(
        pct=Cast(F("score"), FloatField()) * 100.0
        / Cast(F("total_questions"), FloatField())
    ).filter(pct__gte=70).count()

    avg_result = completed_quizzes.filter(total_questions__gt=0).aggregate(
        avg=Avg(
            Cast(F("score"), FloatField()) * 100.0
            / Cast(F("total_questions"), FloatField())
        )
    )
    avg_score = round(avg_result["avg"] or 0.0, 1)

    # Activity stats
    eras_visited = user_progress.filter(era_visited=True).count()
    eras_chatted = user_progress.filter(chat_sessions_count__gt=0).count()
    eras_quizzed = user_progress.filter(quizzes_passed__gt=0).count()

    total_activities = eras_visited + eras_chatted + eras_quizzed
    max_activities = total_eras * 3
    completion_percentage = (
        round((total_activities / max_activities) * 100) if max_activities > 0 else 0
    )

    current_streak = calculate_activity_streak(user)
    total_chat_sessions = ChatSession.objects.filter(user=user).count()

    return {
        "completion_percentage": completion_percentage,
        "eras_visited": eras_visited,
        "eras_chatted": eras_chatted,
        "eras_quizzed": eras_quizzed,
        "total_eras": total_eras,
        "total_quizzes": total_quizzes,
        "quizzes_passed": quizzes_passed,
        "average_score": avg_score,
        "current_streak": current_streak,
        "total_chat_sessions": total_chat_sessions,
        "achievements_unlocked": achievements_unlocked,
        "total_achievements": total_achievements,
    }
