"""URL configuration for the quiz app."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import QuizStatsView, QuizViewSet

app_name = "quiz"

router = DefaultRouter()
router.register(r"quizzes", QuizViewSet, basename="quiz")

urlpatterns = [
    path("", include(router.urls)),
    path("stats/", QuizStatsView.as_view(), name="stats"),
]
