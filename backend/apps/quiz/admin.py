"""Admin configuration for quiz app models."""

from django.contrib import admin

from .models import Quiz, QuizQuestion


class QuizQuestionInline(admin.TabularInline):
    """Inline admin for quiz questions."""

    model = QuizQuestion
    extra = 0
    fields = [
        "order",
        "question_text",
        "question_type",
        "is_correct",
    ]
    readonly_fields = ["order", "question_text", "question_type", "is_correct"]
    can_delete = False


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    """Admin for Quiz model."""

    list_display = [
        "id",
        "user",
        "era",
        "difficulty",
        "score",
        "total_questions",
        "percentage_score",
        "passed",
        "completed_at",
        "created_at",
    ]
    list_filter = [
        "difficulty",
        "era",
        "completed_at",
        "created_at",
    ]
    search_fields = [
        "user__email",
        "era__name",
    ]
    readonly_fields = [
        "created_at",
        "generation_input_tokens",
        "generation_output_tokens",
        "grading_input_tokens",
        "grading_output_tokens",
    ]
    inlines = [QuizQuestionInline]

    def percentage_score(self, obj):
        """Display percentage score."""
        return f"{obj.percentage_score}%"

    def passed(self, obj):
        """Display passed status."""
        return obj.passed

    passed.boolean = True


@admin.register(QuizQuestion)
class QuizQuestionAdmin(admin.ModelAdmin):
    """Admin for QuizQuestion model."""

    list_display = [
        "id",
        "quiz",
        "order",
        "question_type",
        "is_correct",
        "created_at",
    ]
    list_filter = [
        "question_type",
        "is_correct",
        "created_at",
    ]
    search_fields = [
        "question_text",
        "quiz__user__email",
    ]
    readonly_fields = [
        "created_at",
    ]
