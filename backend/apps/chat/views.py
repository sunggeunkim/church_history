"""API views for the chat app.

Provides CRUD endpoints for chat sessions and messages, plus an
async SSE streaming endpoint for real-time AI chat responses.
"""

import json
import logging

from django.http import StreamingHttpResponse
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from .models import ChatMessage, ChatSession
from .serializers import (
    ChatMessageSerializer,
    ChatSessionCreateSerializer,
    ChatSessionSerializer,
    ChatStreamSerializer,
)
from .throttles import ChatBurstThrottle, ChatRateThrottle

logger = logging.getLogger(__name__)


class ChatSessionViewSet(viewsets.ModelViewSet):
    """ViewSet for managing chat sessions.

    Endpoints:
    - GET    /api/chat/sessions/       - List user's chat sessions
    - POST   /api/chat/sessions/       - Create a new session
    - GET    /api/chat/sessions/{id}/  - Retrieve a session
    - PATCH  /api/chat/sessions/{id}/  - Update a session (title, is_archived)
    - DELETE /api/chat/sessions/{id}/  - Delete a session

    All endpoints require authentication and only return sessions
    belonging to the authenticated user.
    """

    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "post", "patch", "delete"]

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == "create":
            return ChatSessionCreateSerializer
        return ChatSessionSerializer

    def get_queryset(self):
        """Return sessions belonging to the authenticated user."""
        return (
            ChatSession.objects.filter(user=self.request.user)
            .select_related("era")
            .prefetch_related("messages")
        )

    def perform_create(self, serializer):
        """Assign the authenticated user to the new session."""
        serializer.save(user=self.request.user)


class ChatMessageListView(ListAPIView):
    """List messages for a specific chat session.

    Endpoint:
    - GET /api/chat/sessions/{session_id}/messages/

    Returns all messages in chronological order for the given session.
    Only accessible by the session owner. Pagination is disabled since
    chat UIs need the full conversation history.
    """

    serializer_class = ChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        """Return messages for the specified session owned by the user."""
        session_id = self.kwargs["session_id"]
        return (
            ChatMessage.objects.filter(
                session_id=session_id,
                session__user=self.request.user,
            )
            .prefetch_related("citations")
            .order_by("created_at")
        )


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def chat_stream(request):
    """Async SSE streaming endpoint for AI chat responses.

    POST /api/chat/stream/
    Body:
    {
        "session_id": 1,
        "message": "Tell me about the early church fathers"
    }

    Returns a streaming response with Server-Sent Events (SSE) containing:
    - data: {"type": "delta", "content": "..."} for each text chunk
    - data: {"type": "done", "message_id": "...", "citations": [...]} on completion
    - data: {"type": "error", "content": "..."} on failure

    Rate limited to 30 messages/hour and 5 messages/minute per user.
    """
    # Validate request data
    serializer = ChatStreamSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    session_id = serializer.validated_data["session_id"]
    message_text = serializer.validated_data["message"]

    # Verify session ownership
    try:
        session = ChatSession.objects.select_related("era").get(
            id=session_id,
            user=request.user,
        )
    except ChatSession.DoesNotExist:
        return Response(
            {"error": "Chat session not found."},
            status=status.HTTP_404_NOT_FOUND,
        )

    # Apply throttling manually for the function-based view
    throttles = [ChatRateThrottle(), ChatBurstThrottle()]
    for throttle in throttles:
        if not throttle.allow_request(request, None):
            wait = throttle.wait()
            return Response(
                {"error": f"Rate limit exceeded. Try again in {int(wait)} seconds."},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

    era = session.era

    async def event_stream():
        """Generate SSE events from the chat service."""
        from .services import stream_chat_response

        try:
            async for event in stream_chat_response(session, message_text, era=era):
                data = json.dumps(event)
                yield f"data: {data}\n\n"
        except Exception:
            logger.exception("Error during chat stream")
            error_event = json.dumps(
                {"type": "error", "content": "An unexpected error occurred."}
            )
            yield f"data: {error_event}\n\n"

    response = StreamingHttpResponse(
        event_stream(),
        content_type="text/event-stream",
    )
    response["X-Accel-Buffering"] = "no"
    response["Cache-Control"] = "no-cache"
    return response
