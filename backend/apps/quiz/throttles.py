"""Rate throttling classes for quiz endpoints.

Provides both sustained and burst rate limiting to prevent
abuse of the OpenAI quiz generation API.
"""

from rest_framework.throttling import UserRateThrottle


class QuizRateThrottle(UserRateThrottle):
    """Sustained rate limit for quiz creation (20 per hour)."""

    scope = "quiz"


class QuizBurstThrottle(UserRateThrottle):
    """Burst rate limit for quiz creation (3 per minute)."""

    scope = "quiz_burst"
