"""Rate throttling classes for chat endpoints.

Provides both sustained and burst rate limiting to prevent
abuse of the AI chat API while allowing normal usage patterns.
"""

from rest_framework.throttling import UserRateThrottle


class ChatRateThrottle(UserRateThrottle):
    """Sustained rate limit for chat messages (30 per hour)."""

    scope = "chat"


class ChatBurstThrottle(UserRateThrottle):
    """Burst rate limit for chat messages (5 per minute)."""

    scope = "chat_burst"
