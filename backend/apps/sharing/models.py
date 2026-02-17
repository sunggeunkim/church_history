"""Social sharing models."""

import secrets
import string

from django.conf import settings
from django.db import models


def generate_share_token(length=8):
    """Generate a cryptographically random base62 share token."""
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


class ShareLink(models.Model):
    """A shareable link to an achievement, quiz result, or progress summary."""

    class ShareType(models.TextChoices):
        ACHIEVEMENT = "achievement", "Achievement"
        QUIZ_RESULT = "quiz_result", "Quiz Result"
        PROGRESS = "progress", "Progress Summary"

    token = models.CharField(max_length=16, unique=True, db_index=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="share_links",
    )
    share_type = models.CharField(max_length=20, choices=ShareType.choices)
    content_snapshot = models.JSONField()
    sharer_display_name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    view_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.sharer_display_name} - {self.get_share_type_display()} ({self.token})"

    def save(self, *args, **kwargs):
        if not self.token:
            for _ in range(5):
                token = generate_share_token()
                if not ShareLink.objects.filter(token=token).exists():
                    self.token = token
                    break
            else:
                raise RuntimeError("Failed to generate unique share token")
        super().save(*args, **kwargs)

    @property
    def share_url(self):
        base_url = getattr(settings, "SHARE_BASE_URL", "http://localhost:8000")
        return f"{base_url}/share/{self.token}"
