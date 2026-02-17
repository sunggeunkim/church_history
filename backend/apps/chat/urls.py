"""URL configuration for the chat app."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "chat"

router = DefaultRouter()
router.register(r"sessions", views.ChatSessionViewSet, basename="session")

urlpatterns = [
    path("", include(router.urls)),
    path(
        "sessions/<int:session_id>/messages/",
        views.ChatMessageListView.as_view(),
        name="session-messages",
    ),
    path("stream/", views.chat_stream, name="chat-stream"),
]
