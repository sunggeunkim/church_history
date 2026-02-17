"""Progress tracking models.

Models for tracking user progress across eras, including achievements and
per-era engagement metrics (visited, chatted, quizzed).
"""

from django.conf import settings
from django.db import models


class UserProgress(models.Model):
    """Per-era progress tracking for a user.

    Tracks user engagement with each era across three dimensions:
    - Era exploration (canvas visit)
    - Chat engagement (at least one chat session)
    - Quiz completion (at least one quiz passed)

    Denormalizes some data (chat count, best score) for efficient queries.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="era_progress",
    )
    era = models.ForeignKey(
        "eras.Era",
        on_delete=models.CASCADE,
        related_name="user_progress",
    )

    # Exploration tracking
    era_visited = models.BooleanField(
        default=False,
        help_text="True if user has expanded this era on canvas",
    )
    first_visited_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="First time user expanded this era",
    )

    # Chat tracking (denormalized)
    chat_sessions_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of chat sessions for this era",
    )
    last_chat_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Most recent chat session for this era",
    )

    # Quiz tracking (denormalized)
    quizzes_completed = models.PositiveIntegerField(
        default=0,
        help_text="Number of completed quizzes for this era",
    )
    quizzes_passed = models.PositiveIntegerField(
        default=0,
        help_text="Number of quizzes passed (70%+) for this era",
    )
    best_quiz_score = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Best percentage score achieved for this era",
    )
    last_quiz_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Most recent quiz completion for this era",
    )

    # Timestamp tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["era__order"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "era"],
                name="progress_userprogress_user_era_uniq",
            ),
        ]
        indexes = [
            models.Index(fields=["user", "updated_at"]),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.era.name}"

    @property
    def completion_percentage(self):
        """Calculate completion percentage for this era (0-100).

        Three activities contribute equally:
        - Era visited: 33.3%
        - Chat initiated: 33.3%
        - Quiz passed: 33.3%
        """
        completed = 0
        if self.era_visited:
            completed += 1
        if self.chat_sessions_count > 0:
            completed += 1
        if self.quizzes_passed > 0:
            completed += 1
        return round((completed / 3) * 100)


class Achievement(models.Model):
    """A predefined achievement that users can unlock.

    Achievements are created via migration and represent milestones
    in the user's learning journey.
    """

    # Achievement types (for categorization)
    class Category(models.TextChoices):
        EXPLORATION = "exploration", "Exploration"
        CHAT = "chat", "Chat"
        QUIZ = "quiz", "Quiz"
        STREAK = "streak", "Streak"
        MASTERY = "mastery", "Mastery"

    slug = models.SlugField(max_length=100, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    category = models.CharField(
        max_length=20,
        choices=Category.choices,
    )
    icon_key = models.CharField(
        max_length=50,
        help_text="Lucide icon name (e.g., 'trophy', 'star', 'target')",
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text="Display order within category",
    )

    class Meta:
        ordering = ["category", "order"]

    def __str__(self):
        return self.name


class UserAchievement(models.Model):
    """Links a user to an unlocked achievement.

    Records when the achievement was unlocked for celebration
    and timeline display.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="achievements",
    )
    achievement = models.ForeignKey(
        Achievement,
        on_delete=models.CASCADE,
        related_name="user_achievements",
    )
    unlocked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-unlocked_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "achievement"],
                name="progress_userachievement_user_achievement_uniq",
            ),
        ]
        indexes = [
            models.Index(fields=["user", "-unlocked_at"]),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.achievement.name}"
