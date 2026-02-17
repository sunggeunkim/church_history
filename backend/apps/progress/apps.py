from django.apps import AppConfig


class ProgressConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.progress"
    verbose_name = "Progress"

    def ready(self):
        """Import signal handlers when app is ready."""
        import apps.progress.signals  # noqa: F401
