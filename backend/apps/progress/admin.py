"""Admin configuration for the progress tracking app."""

from django.contrib import admin

from .models import Achievement, UserAchievement, UserProgress


@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "era",
        "era_visited",
        "chat_sessions_count",
        "quizzes_passed",
        "completion_percentage",
        "updated_at",
    ]
    list_filter = ["era_visited", "era"]
    search_fields = ["user__email", "era__name"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "category", "icon_key", "order"]
    list_filter = ["category"]
    search_fields = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
    list_display = ["user", "achievement", "unlocked_at"]
    list_filter = ["achievement__category"]
    search_fields = ["user__email", "achievement__name"]
    readonly_fields = ["unlocked_at"]
