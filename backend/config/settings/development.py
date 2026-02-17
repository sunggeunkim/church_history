"""
Development-specific Django settings.

DEBUG mode enabled, relaxed CORS, and debug toolbar.
"""

from .base import *  # noqa: F401, F403

DEBUG = True

# Allow all hosts in development
ALLOWED_HOSTS = ["*"]

# CORS - permissive in development
CORS_ALLOW_ALL_ORIGINS = True

# Django Debug Toolbar
INSTALLED_APPS += ["debug_toolbar"]  # noqa: F405
MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")  # noqa: F405
INTERNAL_IPS = ["127.0.0.1", "localhost"]

# Email backend for development
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "DEBUG",
    },
}
