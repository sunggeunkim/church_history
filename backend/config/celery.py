import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

app = Celery("church_history")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
