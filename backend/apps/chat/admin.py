"""Admin configuration for the chat app."""

from django.contrib import admin

from .models import ChatMessage, ChatSession, MessageCitation


class ChatMessageInline(admin.TabularInline):
    """Inline display for messages within a chat session."""

    model = ChatMessage
    extra = 0
    readonly_fields = (
        "role",
        "content",
        "created_at",
        "model_used",
        "input_tokens",
        "output_tokens",
    )
    fields = ("role", "content", "created_at", "model_used", "input_tokens", "output_tokens")
    show_change_link = True


class MessageCitationInline(admin.TabularInline):
    """Inline display for citations within a chat message."""

    model = MessageCitation
    extra = 0
    readonly_fields = ("content_item", "title", "url", "source_name", "order")


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    """Admin interface for ChatSession model."""

    list_display = (
        "id",
        "title",
        "user",
        "era",
        "is_archived",
        "total_input_tokens",
        "total_output_tokens",
        "created_at",
        "updated_at",
    )
    list_filter = ("is_archived", "era", "created_at")
    search_fields = ("title", "user__email", "user__username")
    readonly_fields = (
        "created_at",
        "updated_at",
        "total_input_tokens",
        "total_output_tokens",
    )
    raw_id_fields = ("user", "era")
    inlines = [ChatMessageInline]
    ordering = ["-updated_at"]


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    """Admin interface for ChatMessage model."""

    list_display = (
        "id",
        "session",
        "role",
        "content_preview",
        "model_used",
        "input_tokens",
        "output_tokens",
        "created_at",
    )
    list_filter = ("role", "model_used", "created_at")
    search_fields = ("content", "session__title")
    readonly_fields = (
        "created_at",
        "input_tokens",
        "output_tokens",
        "model_used",
    )
    raw_id_fields = ("session",)
    inlines = [MessageCitationInline]
    ordering = ["-created_at"]

    @admin.display(description="Content Preview")
    def content_preview(self, obj):
        """Return a truncated preview of the message content."""
        if len(obj.content) > 80:
            return obj.content[:80] + "..."
        return obj.content


@admin.register(MessageCitation)
class MessageCitationAdmin(admin.ModelAdmin):
    """Admin interface for MessageCitation model."""

    list_display = ("id", "title", "source_name", "message", "order")
    list_filter = ("source_name",)
    search_fields = ("title", "source_name")
    raw_id_fields = ("message", "content_item")
    ordering = ["message", "order"]
