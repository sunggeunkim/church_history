"""Progress tracking service functions.

Business logic for checking achievements and calculating streaks.
"""

from datetime import timedelta
from typing import List

from django.db.models import F, FloatField
from django.db.models.functions import Cast
from django.utils import timezone

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

    # Exploration achievements
    if slug == "first-visit":
        return UserProgress.objects.filter(user=user, era_visited=True).exists()

    elif slug == "all-eras-visited":
        return UserProgress.objects.filter(user=user, era_visited=True).count() == 6

    # Chat achievements
    elif slug == "first-chat":
        return ChatSession.objects.filter(user=user).exists()

    elif slug == "chat-all-eras":
        return UserProgress.objects.filter(user=user, chat_sessions_count__gt=0).count() == 6

    elif slug == "chat-enthusiast":
        return ChatSession.objects.filter(user=user).count() >= 10

    # Quiz achievements
    elif slug == "first-quiz":
        return Quiz.objects.filter(user=user, completed_at__isnull=False).exists()

    elif slug == "quiz-all-eras":
        return UserProgress.objects.filter(user=user, quizzes_passed__gt=0).count() == 6

    elif slug == "perfect-score":
        # Filter where score == total_questions (100%)
        return Quiz.objects.filter(
            user=user,
            completed_at__isnull=False,
            score=F("total_questions")
        ).exists()

    elif slug == "quiz-master":
        return Quiz.objects.filter(user=user, completed_at__isnull=False).count() >= 20

    elif slug == "high-achiever":
        # Average score >= 85% across all completed quizzes
        completed = Quiz.objects.filter(user=user, completed_at__isnull=False)
        if not completed.exists():
            return False
        # Compute percentage from score/total_questions for each quiz
        total_percentage = 0
        count = 0
        for quiz in completed:
            if quiz.total_questions > 0:
                total_percentage += (quiz.score / quiz.total_questions) * 100
                count += 1
        if count == 0:
            return False
        avg_score = total_percentage / count
        return avg_score >= 85

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
        progress = UserProgress.objects.filter(user=user)
        return (
            progress.filter(era_visited=True).count() == 6 and
            progress.filter(chat_sessions_count__gt=0).count() == 6 and
            progress.filter(quizzes_passed__gt=0).count() == 6
        )

    return False


def calculate_activity_streak(user) -> int:
    """Calculate current activity streak (consecutive days with activity).

    Activity includes: chat session created, quiz completed, or era visited.
    """
    from apps.chat.models import ChatSession
    from apps.quiz.models import Quiz

    today = timezone.now().date()
    current_date = today
    streak = 0

    while True:
        # Check if user had any activity on current_date
        had_activity = False

        # Check chat sessions
        if ChatSession.objects.filter(
            user=user,
            created_at__date=current_date,
        ).exists():
            had_activity = True

        # Check quizzes
        if not had_activity and Quiz.objects.filter(
            user=user,
            completed_at__date=current_date,
        ).exists():
            had_activity = True

        # Check era visits
        if not had_activity and UserProgress.objects.filter(
            user=user,
            first_visited_at__date=current_date,
        ).exists():
            had_activity = True

        if had_activity:
            streak += 1
            current_date -= timedelta(days=1)
        else:
            break

        # Safety: max 365 days lookback
        if streak > 365:
            break

    return streak
