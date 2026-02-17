"""Signal handlers for progress tracking.

Automatically updates UserProgress when users complete chats or quizzes.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.chat.models import ChatSession
from apps.quiz.models import Quiz

from .models import UserProgress


@receiver(post_save, sender=ChatSession)
def update_chat_progress(sender, instance, created, **kwargs):
    """Update UserProgress when a chat session is created."""
    if created and instance.era:
        progress, _ = UserProgress.objects.get_or_create(
            user=instance.user,
            era=instance.era,
        )
        progress.chat_sessions_count = ChatSession.objects.filter(
            user=instance.user,
            era=instance.era,
        ).count()
        progress.last_chat_at = instance.created_at
        progress.save(update_fields=["chat_sessions_count", "last_chat_at", "updated_at"])


@receiver(post_save, sender=Quiz)
def update_quiz_progress(sender, instance, created, **kwargs):
    """Update UserProgress when a quiz is completed."""
    if instance.completed_at and instance.era:
        progress, _ = UserProgress.objects.get_or_create(
            user=instance.user,
            era=instance.era,
        )

        # Count completed and passed quizzes
        era_quizzes = Quiz.objects.filter(
            user=instance.user,
            era=instance.era,
            completed_at__isnull=False,
        )
        progress.quizzes_completed = era_quizzes.count()

        # Count passed quizzes (score == total_questions means 100%, >= 70% passes)
        # We need to compute percentage for each quiz
        passed_count = 0
        best_score = None
        for quiz in era_quizzes:
            if quiz.total_questions > 0:
                percentage = (quiz.score / quiz.total_questions) * 100
                if percentage >= 70:
                    passed_count += 1
                if best_score is None or percentage > best_score:
                    best_score = percentage

        progress.quizzes_passed = passed_count
        progress.best_quiz_score = round(best_score) if best_score is not None else None
        progress.last_quiz_at = instance.completed_at

        progress.save(update_fields=[
            "quizzes_completed",
            "quizzes_passed",
            "best_quiz_score",
            "last_quiz_at",
            "updated_at",
        ])
