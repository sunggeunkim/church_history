"""Progress tracking service functions.

Business logic for checking achievements and calculating streaks.
"""

from datetime import timedelta
from typing import List

from django.db.models import Avg, F, FloatField
from django.db.models.functions import Cast
from django.utils import timezone

from apps.eras.models import Era

from .models import Achievement, UserAchievement, UserProgress


def check_and_unlock_achievements(user) -> List[UserAchievement]:
    """Check all achievements and unlock any newly earned ones.

    Returns list of newly unlocked UserAchievement instances.
    """
    newly_unlocked = []

    # Get all achievements
    achievements = Achievement.objects.all()

    # Get already unlocked achievement IDs
    already_unlocked = set(
        UserAchievement.objects.filter(user=user).values_list("achievement_id", flat=True)
    )

    for achievement in achievements:
        if achievement.id in already_unlocked:
            continue

        # Check if user qualifies for this achievement
        if _check_achievement_criteria(user, achievement):
            # Unlock it
            user_achievement = UserAchievement.objects.create(
                user=user,
                achievement=achievement,
            )
            newly_unlocked.append(user_achievement)

    return newly_unlocked


def _check_achievement_criteria(user, achievement: Achievement) -> bool:
    """Check if user meets criteria for a specific achievement."""
    from apps.chat.models import ChatSession
    from apps.quiz.models import Quiz

    slug = achievement.slug
    total_eras = Era.objects.count()

    # Exploration achievements
    if slug == "first-visit":
        return UserProgress.objects.filter(user=user, era_visited=True).exists()

    elif slug == "all-eras-visited":
        return (
            total_eras > 0
            and UserProgress.objects.filter(user=user, era_visited=True).count() >= total_eras
        )

    # Chat achievements
    elif slug == "first-chat":
        return ChatSession.objects.filter(user=user).exists()

    elif slug == "chat-all-eras":
        return (
            total_eras > 0
            and UserProgress.objects.filter(user=user, chat_sessions_count__gt=0).count()
            >= total_eras
        )

    elif slug == "chat-enthusiast":
        return ChatSession.objects.filter(user=user).count() >= 10

    # Quiz achievements
    elif slug == "first-quiz":
        return Quiz.objects.filter(user=user, completed_at__isnull=False).exists()

    elif slug == "quiz-all-eras":
        return (
            total_eras > 0
            and UserProgress.objects.filter(user=user, quizzes_passed__gt=0).count()
            >= total_eras
        )

    elif slug == "perfect-score":
        # Filter where score == total_questions (100%)
        return Quiz.objects.filter(
            user=user,
            completed_at__isnull=False,
            score=F("total_questions"),
        ).exists()

    elif slug == "quiz-master":
        return Quiz.objects.filter(user=user, completed_at__isnull=False).count() >= 20

    elif slug == "high-achiever":
        # Average score >= 85% across all completed quizzes (DB aggregation)
        result = Quiz.objects.filter(
            user=user,
            completed_at__isnull=False,
            total_questions__gt=0,
        ).aggregate(
            avg=Avg(
                Cast(F("score"), FloatField()) * 100.0
                / Cast(F("total_questions"), FloatField())
            )
        )
        avg_score = result["avg"]
        return avg_score is not None and avg_score >= 85

    # Streak achievements
    elif slug == "three-day-streak":
        streak = calculate_activity_streak(user)
        return streak >= 3

    elif slug == "seven-day-streak":
        streak = calculate_activity_streak(user)
        return streak >= 7

    # Mastery achievements
    elif slug == "complete-beginner":
        # Visited all eras + chatted about all eras + passed quiz in all eras
        if total_eras == 0:
            return False
        progress = UserProgress.objects.filter(user=user)
        return (
            progress.filter(era_visited=True).count() >= total_eras
            and progress.filter(chat_sessions_count__gt=0).count() >= total_eras
            and progress.filter(quizzes_passed__gt=0).count() >= total_eras
        )

    return False


def calculate_activity_streak(user) -> int:
    """Calculate current activity streak (consecutive days with activity).

    Activity includes: chat session created, quiz completed, or era visited.
    Fetches all activity dates in 3 queries, then computes streak in Python.
    """
    from apps.chat.models import ChatSession
    from apps.quiz.models import Quiz

    # Gather all unique activity dates in 3 queries
    chat_dates = set(
        ChatSession.objects.filter(user=user).values_list("created_at__date", flat=True)
    )
    quiz_dates = set(
        Quiz.objects.filter(user=user, completed_at__isnull=False).values_list(
            "completed_at__date", flat=True
        )
    )
    visit_dates = set(
        UserProgress.objects.filter(
            user=user, first_visited_at__isnull=False
        ).values_list("first_visited_at__date", flat=True)
    )
    all_dates = chat_dates | quiz_dates | visit_dates

    if not all_dates:
        return 0

    today = timezone.now().date()
    streak = 0
    current_date = today

    while current_date in all_dates:
        streak += 1
        current_date -= timedelta(days=1)
        if streak > 365:
            break

    return streak
