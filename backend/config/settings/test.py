"""
Test-specific Django settings.

Uses SQLite for fast test execution without requiring PostgreSQL.
"""

from .base import *  # noqa: F401, F403

DEBUG = False

# Use SQLite for tests (no PostgreSQL required)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Faster password hashing for tests
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Email backend for tests
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
