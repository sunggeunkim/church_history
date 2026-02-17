"""Chat session models for AI chat and RAG.

Defines models for managing chat sessions, messages, and source citations
for the Toledot church history AI teaching assistant.
"""

from django.conf import settings
from django.db import models


class ChatSession(models.Model):
    """A conversation session between a user and the AI assistant.

    Tracks the full conversation history, associated era context,
    and cumulative token usage for billing/analytics.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="chat_sessions",
    )
    title = models.CharField(max_length=255, default="New Chat")
    era = models.ForeignKey(
        "eras.Era",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="chat_sessions",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_archived = models.BooleanField(default=False)
    total_input_tokens = models.PositiveIntegerField(default=0)
    total_output_tokens = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-updated_at"]
        indexes = [
            models.Index(fields=["-updated_at"]),
            models.Index(fields=["user", "-updated_at"]),
        ]

    def __str__(self):
        return f"{self.title} ({self.user})"

    @property
    def total_tokens(self):
        """Return the total token count for this session."""
        return self.total_input_tokens + self.total_output_tokens


class ChatMessage(models.Model):
    """A single message within a chat session.

    Stores the message content, role (user or assistant), token usage,
    and references to any content chunks used for RAG retrieval.
    """

    class Role(models.TextChoices):
        USER = "user", "User"
        ASSISTANT = "assistant", "Assistant"

    session = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    role = models.CharField(max_length=10, choices=Role.choices)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    model_used = models.CharField(max_length=50, blank=True)
    input_tokens = models.PositiveIntegerField(default=0)
    output_tokens = models.PositiveIntegerField(default=0)
    retrieved_chunks = models.ManyToManyField(
        "content.ContentChunk",
        blank=True,
        related_name="chat_messages",
    )

    class Meta:
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["session", "created_at"]),
        ]

    def __str__(self):
        preview = self.content[:50] + "..." if len(self.content) > 50 else self.content
        return f"{self.get_role_display()}: {preview}"


class MessageCitation(models.Model):
    """A citation linking an assistant message to a source content item.

    Tracks which sources were referenced in a response, providing
    transparency and traceability for AI-generated answers.
    """

    message = models.ForeignKey(
        ChatMessage,
        on_delete=models.CASCADE,
        related_name="citations",
    )
    content_item = models.ForeignKey(
        "content.ContentItem",
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=500)
    url = models.URLField(max_length=500, blank=True)
    source_name = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]
        indexes = [
            models.Index(fields=["message", "order"]),
        ]

    def __str__(self):
        return f"Citation: {self.title} (message #{self.message_id})"
