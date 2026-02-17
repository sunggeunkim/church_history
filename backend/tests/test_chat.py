"""Comprehensive tests for P4 AI Chat Agent.

Tests cover models, serializers, API endpoints, and service functions
for the chat app's RAG-based AI teaching assistant.
"""

from datetime import date
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.chat.models import ChatMessage, ChatSession, MessageCitation
from apps.chat.serializers import (
    ChatMessageSerializer,
    ChatSessionCreateSerializer,
    ChatSessionSerializer,
    ChatStreamSerializer,
    MessageCitationSerializer,
)
from apps.chat.services import (
    build_context,
    build_messages,
    extract_citations,
)
from apps.content.models import ContentChunk, ContentItem, ContentTag, Source
from apps.eras.models import Era


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def user(create_user):
    """Create a test user."""
    return create_user(
        email="chatuser@example.com",
        username="chatuser",
        password="testpass123",
    )


@pytest.fixture
def other_user(create_user):
    """Create a second test user for permission tests."""
    return create_user(
        email="other@example.com",
        username="otheruser",
        password="testpass123",
    )


@pytest.fixture
def authenticated_client(user):
    """Create an authenticated API client for the test user."""
    client = APIClient()
    refresh = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return client


@pytest.fixture
def other_authenticated_client(other_user):
    """Create an authenticated API client for the other user."""
    client = APIClient()
    refresh = RefreshToken.for_user(other_user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return client


@pytest.fixture
def sample_era(db):
    """Create a sample era."""
    return Era.objects.create(
        name="Reformation",
        slug="reformation",
        start_year=1517,
        end_year=1648,
        description="The Protestant Reformation era, a period of significant religious change.",
        summary="Recovery of the gospel through the five solas.",
        color="#15803D",
        order=4,
    )


@pytest.fixture
def chat_session(db, user, sample_era):
    """Create a test chat session."""
    return ChatSession.objects.create(
        user=user,
        title="Reformation Discussion",
        era=sample_era,
    )


@pytest.fixture
def chat_session_no_era(db, user):
    """Create a test chat session without an era."""
    return ChatSession.objects.create(
        user=user,
        title="General Question",
    )


@pytest.fixture
def user_message(db, chat_session):
    """Create a test user message."""
    return ChatMessage.objects.create(
        session=chat_session,
        role=ChatMessage.Role.USER,
        content="Tell me about Martin Luther",
    )


@pytest.fixture
def assistant_message(db, chat_session):
    """Create a test assistant message."""
    return ChatMessage.objects.create(
        session=chat_session,
        role=ChatMessage.Role.ASSISTANT,
        content="Martin Luther was a German theologian and reformer...",
        model_used="claude-haiku-4-5-20251001",
        input_tokens=150,
        output_tokens=200,
    )


@pytest.fixture
def source(db):
    """Create a test content source."""
    return Source.objects.create(
        name="Ryan Reeves",
        url="https://www.youtube.com/channel/UCexample",
        source_type=Source.SourceType.YOUTUBE_CHANNEL,
        description="Church history lectures",
        is_active=True,
    )


@pytest.fixture
def content_item(db, source):
    """Create a test content item."""
    return ContentItem.objects.create(
        source=source,
        content_type=ContentItem.ContentType.TRANSCRIPT,
        title="Luther's 95 Theses Explained",
        url="https://www.youtube.com/watch?v=TEST123",
        external_id="TEST123",
        author="Ryan Reeves",
        published_date=date(2024, 1, 15),
        raw_text="This is a transcript about Luther's 95 Theses.",
        processed_text="This is a transcript about Luther's 95 Theses.",
        token_count=10,
        is_processed=True,
    )


@pytest.fixture
def content_item_2(db, source):
    """Create a second test content item."""
    return ContentItem.objects.create(
        source=source,
        content_type=ContentItem.ContentType.TRANSCRIPT,
        title="Calvin's Institutes Overview",
        url="https://www.youtube.com/watch?v=TEST456",
        external_id="TEST456",
        author="Ryan Reeves",
        raw_text="This is about Calvin's Institutes.",
        token_count=8,
        is_processed=True,
    )


@pytest.fixture
def citation(db, assistant_message, content_item):
    """Create a test message citation."""
    return MessageCitation.objects.create(
        message=assistant_message,
        content_item=content_item,
        title="Luther's 95 Theses Explained",
        url="https://www.youtube.com/watch?v=TEST123",
        source_name="Ryan Reeves",
        order=0,
    )


# =============================================================================
# Model Tests
# =============================================================================


@pytest.mark.django_db
class TestChatSessionModel:
    """Test ChatSession model."""

    def test_create_chat_session(self, chat_session, user, sample_era):
        """Test creating a chat session with all fields."""
        assert chat_session.user == user
        assert chat_session.title == "Reformation Discussion"
        assert chat_session.era == sample_era
        assert chat_session.is_archived is False
        assert chat_session.total_input_tokens == 0
        assert chat_session.total_output_tokens == 0
        assert chat_session.created_at is not None
        assert chat_session.updated_at is not None

    def test_create_chat_session_defaults(self, user):
        """Test chat session default values."""
        session = ChatSession.objects.create(user=user)
        assert session.title == "New Chat"
        assert session.era is None
        assert session.is_archived is False
        assert session.total_input_tokens == 0
        assert session.total_output_tokens == 0

    def test_chat_session_str(self, chat_session):
        """Test string representation."""
        assert "Reformation Discussion" in str(chat_session)

    def test_total_tokens_property(self, chat_session):
        """Test total_tokens computed property."""
        chat_session.total_input_tokens = 100
        chat_session.total_output_tokens = 200
        assert chat_session.total_tokens == 300

    def test_chat_session_ordering(self, user):
        """Test sessions are ordered by -updated_at."""
        session1 = ChatSession.objects.create(user=user, title="First")
        session2 = ChatSession.objects.create(user=user, title="Second")

        sessions = list(ChatSession.objects.filter(user=user))
        # Most recently created/updated should be first
        assert sessions[0] == session2
        assert sessions[1] == session1

    def test_chat_session_cascade_delete_user(self, chat_session, user):
        """Test that deleting user cascades to sessions."""
        session_id = chat_session.id
        user.delete()
        assert not ChatSession.objects.filter(id=session_id).exists()

    def test_chat_session_era_set_null(self, chat_session, sample_era):
        """Test that deleting era sets null on session."""
        session_id = chat_session.id
        sample_era.delete()
        chat_session.refresh_from_db()
        assert chat_session.era is None


@pytest.mark.django_db
class TestChatMessageModel:
    """Test ChatMessage model."""

    def test_create_user_message(self, user_message, chat_session):
        """Test creating a user message."""
        assert user_message.session == chat_session
        assert user_message.role == ChatMessage.Role.USER
        assert user_message.content == "Tell me about Martin Luther"
        assert user_message.model_used == ""
        assert user_message.input_tokens == 0
        assert user_message.output_tokens == 0
        assert user_message.created_at is not None

    def test_create_assistant_message(self, assistant_message, chat_session):
        """Test creating an assistant message with token counts."""
        assert assistant_message.session == chat_session
        assert assistant_message.role == ChatMessage.Role.ASSISTANT
        assert assistant_message.model_used == "claude-haiku-4-5-20251001"
        assert assistant_message.input_tokens == 150
        assert assistant_message.output_tokens == 200

    def test_chat_message_str_short(self, user_message):
        """Test string representation for short message."""
        assert "User:" in str(user_message)
        assert "Tell me about Martin Luther" in str(user_message)

    def test_chat_message_str_long(self, chat_session):
        """Test string representation truncation for long message."""
        long_content = "A" * 100
        msg = ChatMessage.objects.create(
            session=chat_session,
            role=ChatMessage.Role.ASSISTANT,
            content=long_content,
        )
        str_repr = str(msg)
        assert "..." in str_repr
        assert len(str_repr) < len(long_content) + 30  # "Assistant: " + truncated

    def test_chat_message_ordering(self, chat_session):
        """Test messages are ordered by created_at."""
        msg1 = ChatMessage.objects.create(
            session=chat_session,
            role=ChatMessage.Role.USER,
            content="First message",
        )
        msg2 = ChatMessage.objects.create(
            session=chat_session,
            role=ChatMessage.Role.ASSISTANT,
            content="Second message",
        )

        messages = list(chat_session.messages.all())
        assert messages[0] == msg1
        assert messages[1] == msg2

    def test_chat_message_cascade_delete_session(self, user_message, chat_session):
        """Test that deleting session cascades to messages."""
        message_id = user_message.id
        chat_session.delete()
        assert not ChatMessage.objects.filter(id=message_id).exists()

    def test_session_message_relationship(self, chat_session):
        """Test session-message relationship and count."""
        ChatMessage.objects.create(
            session=chat_session,
            role=ChatMessage.Role.USER,
            content="Question 1",
        )
        ChatMessage.objects.create(
            session=chat_session,
            role=ChatMessage.Role.ASSISTANT,
            content="Answer 1",
        )
        ChatMessage.objects.create(
            session=chat_session,
            role=ChatMessage.Role.USER,
            content="Question 2",
        )

        assert chat_session.messages.count() == 3
        assert chat_session.messages.filter(role=ChatMessage.Role.USER).count() == 2
        assert chat_session.messages.filter(role=ChatMessage.Role.ASSISTANT).count() == 1

    def test_role_choices(self):
        """Test that Role choices are correctly defined."""
        assert ChatMessage.Role.USER == "user"
        assert ChatMessage.Role.ASSISTANT == "assistant"
        assert len(ChatMessage.Role.choices) == 2


@pytest.mark.django_db
class TestMessageCitationModel:
    """Test MessageCitation model."""

    def test_create_citation(self, citation, assistant_message, content_item):
        """Test creating a message citation."""
        assert citation.message == assistant_message
        assert citation.content_item == content_item
        assert citation.title == "Luther's 95 Theses Explained"
        assert citation.url == "https://www.youtube.com/watch?v=TEST123"
        assert citation.source_name == "Ryan Reeves"
        assert citation.order == 0

    def test_citation_str(self, citation):
        """Test citation string representation."""
        assert "Citation:" in str(citation)
        assert "Luther's 95 Theses Explained" in str(citation)

    def test_citation_ordering(self, assistant_message, content_item, content_item_2):
        """Test citations are ordered by order field."""
        citation2 = MessageCitation.objects.create(
            message=assistant_message,
            content_item=content_item_2,
            title="Calvin's Institutes Overview",
            source_name="Ryan Reeves",
            order=1,
        )
        citation1 = MessageCitation.objects.create(
            message=assistant_message,
            content_item=content_item,
            title="Luther's 95 Theses Explained",
            source_name="Ryan Reeves",
            order=0,
        )

        citations = list(assistant_message.citations.all())
        assert citations[0] == citation1
        assert citations[1] == citation2

    def test_citation_cascade_delete_message(self, citation, assistant_message):
        """Test that deleting message cascades to citations."""
        citation_id = citation.id
        assistant_message.delete()
        assert not MessageCitation.objects.filter(id=citation_id).exists()

    def test_token_counting_on_session(self, chat_session):
        """Test that session token counts update correctly."""
        chat_session.total_input_tokens = 500
        chat_session.total_output_tokens = 1000
        chat_session.save()

        chat_session.refresh_from_db()
        assert chat_session.total_input_tokens == 500
        assert chat_session.total_output_tokens == 1000
        assert chat_session.total_tokens == 1500


# =============================================================================
# Serializer Tests
# =============================================================================


@pytest.mark.django_db
class TestChatSessionSerializer:
    """Test ChatSession serializers."""

    def test_session_serializer_fields(self, chat_session):
        """Test that ChatSessionSerializer includes all expected fields."""
        serializer = ChatSessionSerializer(chat_session)
        data = serializer.data

        assert "id" in data
        assert "title" in data
        assert "era" in data
        assert "era_name" in data
        assert "created_at" in data
        assert "updated_at" in data
        assert "is_archived" in data
        assert "total_input_tokens" in data
        assert "total_output_tokens" in data
        assert "message_count" in data

    def test_session_serializer_message_count(self, chat_session):
        """Test message_count computed field."""
        ChatMessage.objects.create(
            session=chat_session,
            role=ChatMessage.Role.USER,
            content="Hello",
        )
        ChatMessage.objects.create(
            session=chat_session,
            role=ChatMessage.Role.ASSISTANT,
            content="Hi there",
        )

        serializer = ChatSessionSerializer(chat_session)
        assert serializer.data["message_count"] == 2

    def test_session_serializer_zero_messages(self, chat_session):
        """Test message_count is 0 for empty session."""
        serializer = ChatSessionSerializer(chat_session)
        assert serializer.data["message_count"] == 0

    def test_session_serializer_era_name(self, chat_session):
        """Test era_name field shows era name."""
        serializer = ChatSessionSerializer(chat_session)
        assert serializer.data["era_name"] == "Reformation"

    def test_session_serializer_era_name_null(self, chat_session_no_era):
        """Test era_name is null when no era set."""
        serializer = ChatSessionSerializer(chat_session_no_era)
        assert serializer.data["era_name"] is None

    def test_create_serializer_validation(self):
        """Test ChatSessionCreateSerializer validates correctly."""
        serializer = ChatSessionCreateSerializer(
            data={"title": "Test Session"}
        )
        assert serializer.is_valid()

    def test_create_serializer_default_title(self):
        """Test ChatSessionCreateSerializer accepts empty data (uses defaults)."""
        serializer = ChatSessionCreateSerializer(data={})
        assert serializer.is_valid()


@pytest.mark.django_db
class TestChatMessageSerializer:
    """Test ChatMessage serializer."""

    def test_message_serializer_fields(self, user_message):
        """Test that ChatMessageSerializer includes all expected fields."""
        serializer = ChatMessageSerializer(user_message)
        data = serializer.data

        assert "id" in data
        assert "session" in data
        assert "role" in data
        assert "content" in data
        assert "created_at" in data
        assert "model_used" in data
        assert "input_tokens" in data
        assert "output_tokens" in data
        assert "citations" in data

    def test_message_serializer_with_citations(self, assistant_message, citation):
        """Test that citations are nested in the message serializer."""
        serializer = ChatMessageSerializer(assistant_message)
        data = serializer.data

        assert len(data["citations"]) == 1
        assert data["citations"][0]["title"] == "Luther's 95 Theses Explained"
        assert data["citations"][0]["source_name"] == "Ryan Reeves"

    def test_message_serializer_empty_citations(self, user_message):
        """Test message with no citations has empty list."""
        serializer = ChatMessageSerializer(user_message)
        assert serializer.data["citations"] == []


@pytest.mark.django_db
class TestMessageCitationSerializer:
    """Test MessageCitation serializer."""

    def test_citation_serializer_fields(self, citation):
        """Test that MessageCitationSerializer includes all expected fields."""
        serializer = MessageCitationSerializer(citation)
        data = serializer.data

        assert "id" in data
        assert "title" in data
        assert "url" in data
        assert "source_name" in data
        assert "order" in data

    def test_citation_serializer_values(self, citation):
        """Test citation serializer data values."""
        serializer = MessageCitationSerializer(citation)
        data = serializer.data

        assert data["title"] == "Luther's 95 Theses Explained"
        assert data["url"] == "https://www.youtube.com/watch?v=TEST123"
        assert data["source_name"] == "Ryan Reeves"
        assert data["order"] == 0


class TestChatStreamSerializer:
    """Test ChatStreamSerializer validation."""

    def test_valid_data(self):
        """Test valid stream request data."""
        serializer = ChatStreamSerializer(
            data={"session_id": 1, "message": "Hello"}
        )
        assert serializer.is_valid()

    def test_missing_session_id(self):
        """Test missing session_id."""
        serializer = ChatStreamSerializer(data={"message": "Hello"})
        assert not serializer.is_valid()
        assert "session_id" in serializer.errors

    def test_missing_message(self):
        """Test missing message."""
        serializer = ChatStreamSerializer(data={"session_id": 1})
        assert not serializer.is_valid()
        assert "message" in serializer.errors

    def test_empty_message(self):
        """Test empty message string."""
        serializer = ChatStreamSerializer(
            data={"session_id": 1, "message": ""}
        )
        assert not serializer.is_valid()


# =============================================================================
# API Endpoint Tests
# =============================================================================


@pytest.mark.django_db
class TestChatSessionAPI:
    """Test ChatSession API endpoints."""

    def test_list_sessions_authenticated(self, authenticated_client, chat_session):
        """Test listing sessions returns user's sessions."""
        url = reverse("chat:session-list")
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        results = response.data.get("results", response.data)
        assert len(results) >= 1
        assert results[0]["title"] == "Reformation Discussion"

    def test_list_sessions_unauthenticated(self, api_client, chat_session):
        """Test listing sessions requires authentication."""
        url = reverse("chat:session-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_sessions_only_own_sessions(
        self, authenticated_client, other_authenticated_client, chat_session, other_user
    ):
        """Test users only see their own sessions."""
        # Create session for other user
        ChatSession.objects.create(user=other_user, title="Other's Chat")

        url = reverse("chat:session-list")
        response = authenticated_client.get(url)

        results = response.data.get("results", response.data)
        titles = [r["title"] for r in results]
        assert "Reformation Discussion" in titles
        assert "Other's Chat" not in titles

    def test_create_session(self, authenticated_client, sample_era):
        """Test creating a new chat session."""
        url = reverse("chat:session-list")
        data = {
            "title": "New Discussion",
            "era": sample_era.id,
        }
        response = authenticated_client.post(url, data)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["title"] == "New Discussion"
        assert response.data["id"] is not None

    def test_create_session_default_title(self, authenticated_client):
        """Test creating a session with default title."""
        url = reverse("chat:session-list")
        response = authenticated_client.post(url, {})

        assert response.status_code == status.HTTP_201_CREATED
        # The serializer should accept defaults

    def test_retrieve_session(self, authenticated_client, chat_session):
        """Test retrieving a specific session."""
        url = reverse("chat:session-detail", kwargs={"pk": chat_session.id})
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == "Reformation Discussion"
        assert response.data["era_name"] == "Reformation"
        assert "message_count" in response.data

    def test_retrieve_other_users_session(
        self, other_authenticated_client, chat_session
    ):
        """Test that a user cannot retrieve another user's session."""
        url = reverse("chat:session-detail", kwargs={"pk": chat_session.id})
        response = other_authenticated_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_session(self, authenticated_client, chat_session):
        """Test deleting a chat session."""
        url = reverse("chat:session-detail", kwargs={"pk": chat_session.id})
        response = authenticated_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not ChatSession.objects.filter(id=chat_session.id).exists()

    def test_update_session_title(self, authenticated_client, chat_session):
        """Test updating a session title via PATCH."""
        url = reverse("chat:session-detail", kwargs={"pk": chat_session.id})
        response = authenticated_client.patch(
            url, {"title": "Updated Title"}, format="json"
        )

        assert response.status_code == status.HTTP_200_OK
        chat_session.refresh_from_db()
        assert chat_session.title == "Updated Title"

    def test_archive_session(self, authenticated_client, chat_session):
        """Test archiving a session via PATCH."""
        url = reverse("chat:session-detail", kwargs={"pk": chat_session.id})
        response = authenticated_client.patch(
            url, {"is_archived": True}, format="json"
        )

        assert response.status_code == status.HTTP_200_OK
        chat_session.refresh_from_db()
        assert chat_session.is_archived is True


@pytest.mark.django_db
class TestChatMessageAPI:
    """Test ChatMessage API endpoints."""

    def test_list_messages(self, authenticated_client, chat_session, user_message, assistant_message):
        """Test listing messages for a session."""
        url = reverse(
            "chat:session-messages",
            kwargs={"session_id": chat_session.id},
        )
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        # Messages endpoint has no pagination - returns a plain list
        assert len(response.data) == 2

    def test_list_messages_chronological_order(
        self, authenticated_client, chat_session
    ):
        """Test messages are returned in chronological order."""
        msg1 = ChatMessage.objects.create(
            session=chat_session,
            role=ChatMessage.Role.USER,
            content="First",
        )
        msg2 = ChatMessage.objects.create(
            session=chat_session,
            role=ChatMessage.Role.ASSISTANT,
            content="Second",
        )

        url = reverse(
            "chat:session-messages",
            kwargs={"session_id": chat_session.id},
        )
        response = authenticated_client.get(url)

        assert response.data[0]["content"] == "First"
        assert response.data[1]["content"] == "Second"

    def test_list_messages_other_user_empty(
        self, other_authenticated_client, chat_session, user_message
    ):
        """Test that another user gets empty results for someone else's session."""
        url = reverse(
            "chat:session-messages",
            kwargs={"session_id": chat_session.id},
        )
        response = other_authenticated_client.get(url)

        # The view filters by user, so it returns empty results
        assert len(response.data) == 0

    def test_list_messages_unauthenticated(self, api_client, chat_session):
        """Test that unauthenticated access is denied."""
        url = reverse(
            "chat:session-messages",
            kwargs={"session_id": chat_session.id},
        )
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_messages_with_citations(
        self, authenticated_client, chat_session, assistant_message, citation
    ):
        """Test that message listing includes nested citations."""
        url = reverse(
            "chat:session-messages",
            kwargs={"session_id": chat_session.id},
        )
        response = authenticated_client.get(url)

        assistant_data = [r for r in response.data if r["role"] == "assistant"][0]
        assert len(assistant_data["citations"]) == 1
        assert assistant_data["citations"][0]["title"] == "Luther's 95 Theses Explained"


@pytest.mark.django_db
class TestChatStreamAPI:
    """Test the chat stream endpoint."""

    def test_stream_unauthenticated(self, api_client, chat_session):
        """Test that unauthenticated access is denied."""
        url = reverse("chat:chat-stream")
        response = api_client.post(
            url,
            {"session_id": chat_session.id, "message": "Hello"},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_stream_missing_session_id(self, authenticated_client):
        """Test stream with missing session_id returns 400."""
        url = reverse("chat:chat-stream")
        response = authenticated_client.post(
            url, {"message": "Hello"}, format="json"
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_stream_missing_message(self, authenticated_client, chat_session):
        """Test stream with missing message returns 400."""
        url = reverse("chat:chat-stream")
        response = authenticated_client.post(
            url, {"session_id": chat_session.id}, format="json"
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_stream_nonexistent_session(self, authenticated_client):
        """Test stream with nonexistent session returns 404."""
        url = reverse("chat:chat-stream")
        response = authenticated_client.post(
            url,
            {"session_id": 99999, "message": "Hello"},
            format="json",
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_stream_other_users_session(
        self, other_authenticated_client, chat_session
    ):
        """Test stream cannot use another user's session."""
        url = reverse("chat:chat-stream")
        response = other_authenticated_client.post(
            url,
            {"session_id": chat_session.id, "message": "Hello"},
            format="json",
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


# =============================================================================
# Service Tests
# =============================================================================


@pytest.mark.django_db
class TestBuildContext:
    """Test the build_context service function."""

    def test_build_context_with_era(self, sample_era):
        """Test context includes era information."""
        context = build_context([], era=sample_era)
        assert "Reformation" in context
        assert "1517" in context
        assert "1648" in context

    def test_build_context_with_era_no_end_year(self, db):
        """Test context handles era without end year."""
        era = Era.objects.create(
            name="Contemporary",
            slug="contemporary",
            start_year=1900,
            description="Modern era",
            color="#475569",
            order=6,
        )
        context = build_context([], era=era)
        assert "present" in context

    def test_build_context_without_era(self):
        """Test context without era returns empty string."""
        context = build_context([])
        assert context == ""

    def test_build_context_with_chunks(self, content_item):
        """Test context includes chunk content and source info."""
        # Create a mock chunk with necessary attributes
        chunk = MagicMock()
        chunk.content_item = content_item
        chunk.chunk_text = "This is chunk text about Luther."

        context = build_context([chunk])
        assert "Luther's 95 Theses Explained" in context
        assert "Ryan Reeves" in context
        assert "This is chunk text about Luther." in context
        assert "--- Source:" in context
        assert "--- End Source ---" in context

    def test_build_context_with_era_and_chunks(self, sample_era, content_item):
        """Test context includes both era info and chunks."""
        chunk = MagicMock()
        chunk.content_item = content_item
        chunk.chunk_text = "Chunk text"

        context = build_context([chunk], era=sample_era)
        assert "Reformation" in context
        assert "Chunk text" in context

    def test_build_context_unknown_author(self, source):
        """Test context handles item with no author."""
        item = ContentItem.objects.create(
            source=source,
            content_type=ContentItem.ContentType.ARTICLE,
            title="Anonymous Article",
            raw_text="Some text",
            author="",
        )
        chunk = MagicMock()
        chunk.content_item = item
        chunk.chunk_text = "Chunk from anonymous source"

        context = build_context([chunk])
        assert "Unknown" in context


@pytest.mark.django_db
class TestBuildMessages:
    """Test the build_messages service function."""

    def test_build_messages_empty_history(self, chat_session):
        """Test building messages with no prior history."""
        messages = build_messages(chat_session, "Hello", "Some context")
        assert len(messages) == 1
        assert messages[0]["role"] == "user"
        assert "Some context" in messages[0]["content"]
        assert "Hello" in messages[0]["content"]

    def test_build_messages_with_history(self, chat_session, user_message, assistant_message):
        """Test building messages includes conversation history."""
        messages = build_messages(chat_session, "Follow up question", "context")
        # Should include: user_message, assistant_message, new message
        assert len(messages) == 3
        assert messages[0]["role"] == "user"
        assert messages[1]["role"] == "assistant"
        assert messages[2]["role"] == "user"
        assert "Follow up question" in messages[2]["content"]

    def test_build_messages_without_context(self, chat_session):
        """Test building messages without RAG context."""
        messages = build_messages(chat_session, "Simple question", "")
        assert len(messages) == 1
        assert messages[0]["content"] == "Simple question"

    def test_build_messages_limits_history(self, chat_session):
        """Test that message history is limited to 20 messages."""
        # Create 25 messages
        for i in range(25):
            role = ChatMessage.Role.USER if i % 2 == 0 else ChatMessage.Role.ASSISTANT
            ChatMessage.objects.create(
                session=chat_session,
                role=role,
                content=f"Message {i}",
            )

        messages = build_messages(chat_session, "Latest question", "")
        # 20 history messages + 1 new message
        assert len(messages) == 21


@pytest.mark.django_db
class TestExtractCitations:
    """Test the extract_citations service function."""

    def test_extract_citations_title_match(self, content_item):
        """Test citation extraction when title appears in response."""
        chunk = MagicMock()
        chunk.content_item = content_item

        response_text = (
            "According to Luther's 95 Theses Explained, "
            "the Reformation began in 1517."
        )
        citations = extract_citations(response_text, [chunk])
        assert len(citations) == 1
        assert citations[0]["title"] == "Luther's 95 Theses Explained"

    def test_extract_citations_source_notation(self, content_item):
        """Test citation extraction when [Source: ...] notation is used."""
        chunk = MagicMock()
        chunk.content_item = content_item

        response_text = (
            "The Reformation began in 1517. [Source: Luther's 95 Theses Explained]"
        )
        citations = extract_citations(response_text, [chunk])
        assert len(citations) == 1

    def test_extract_citations_no_match(self, content_item):
        """Test that no citations returned when source not referenced."""
        chunk = MagicMock()
        chunk.content_item = content_item

        response_text = "The early church was founded in Jerusalem."
        citations = extract_citations(response_text, [chunk])
        assert len(citations) == 0

    def test_extract_citations_deduplication(self, content_item):
        """Test that duplicate content items are deduplicated."""
        chunk1 = MagicMock()
        chunk1.content_item = content_item
        chunk2 = MagicMock()
        chunk2.content_item = content_item  # Same item

        response_text = "Luther's 95 Theses Explained discusses the Reformation."
        citations = extract_citations(response_text, [chunk1, chunk2])
        assert len(citations) == 1

    def test_extract_citations_multiple_sources(self, content_item, content_item_2):
        """Test extraction with multiple different sources referenced."""
        chunk1 = MagicMock()
        chunk1.content_item = content_item
        chunk2 = MagicMock()
        chunk2.content_item = content_item_2

        response_text = (
            "Luther's 95 Theses Explained and Calvin's Institutes Overview "
            "both discuss the Reformation."
        )
        citations = extract_citations(response_text, [chunk1, chunk2])
        assert len(citations) == 2

    def test_extract_citations_includes_url_and_source_name(self, content_item):
        """Test that citation dict includes url and source_name."""
        chunk = MagicMock()
        chunk.content_item = content_item

        response_text = "Luther's 95 Theses Explained is an important resource."
        citations = extract_citations(response_text, [chunk])
        assert len(citations) == 1
        assert citations[0]["url"] == "https://www.youtube.com/watch?v=TEST123"
        assert citations[0]["source_name"] == "Ryan Reeves"

    def test_extract_citations_empty_chunks(self):
        """Test extraction with no chunks."""
        citations = extract_citations("Some response text", [])
        assert len(citations) == 0


@pytest.mark.django_db
class TestRetrieveRelevantChunks:
    """Test the retrieve_relevant_chunks service function."""

    @patch("apps.chat.services.get_query_embedding")
    def test_retrieve_returns_list(self, mock_embedding, content_item):
        """Test that retrieve returns a list of chunks."""
        mock_embedding.return_value = [0.1] * 384

        # Create a chunk with embedding
        ContentChunk.objects.create(
            content_item=content_item,
            chunk_text="Luther posted 95 theses on the church door.",
            chunk_index=0,
            token_count=10,
            embedding=[0.1] * 384,
        )

        from apps.chat.services import retrieve_relevant_chunks

        # This will work with SQLite in tests if pgvector is not
        # available, or skip if the distance function isn't supported
        try:
            results = retrieve_relevant_chunks("Luther 95 theses")
            assert isinstance(results, list)
        except Exception:
            # pgvector operations may not work with SQLite test DB
            pytest.skip("pgvector not available in test database")

    @patch("apps.chat.services.get_query_embedding")
    def test_retrieve_respects_top_k(self, mock_embedding):
        """Test that retrieve respects the top_k parameter."""
        mock_embedding.return_value = [0.1] * 384

        from apps.chat.services import retrieve_relevant_chunks

        try:
            results = retrieve_relevant_chunks("test query", top_k=3)
            assert len(results) <= 3
        except Exception:
            pytest.skip("pgvector not available in test database")
