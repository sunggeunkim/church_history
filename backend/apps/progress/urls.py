"""URL configuration for the progress tracking app."""

from django.urls import path

from . import views

app_name = "progress"

urlpatterns = [
    path("summary/", views.ProgressSummaryView.as_view(), name="summary"),
    path(
        "mark-era-visited/",
        views.MarkEraVisitedView.as_view(),
        name="mark-era-visited",
    ),
    path(
        "achievements/",
        views.AchievementListView.as_view(),
        name="achievements",
    ),
    path(
        "check-achievements/",
        views.CheckAchievementsView.as_view(),
        name="check-achievements",
    ),
]
