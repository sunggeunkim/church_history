"""Comprehensive tests for P2 Content Scraping Pipeline."""

import pytest
from datetime import date
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import IntegrityError

from apps.content.models import (
    Source,
    ContentItem,
    ContentTag,
    ContentItemTag,
    ContentChunk,
)
from apps.content.utils import chunk_text, clean_transcript, count_tokens


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def source(db):
    """Create a test YouTube channel source."""
    return Source.objects.create(
        name="Ryan Reeves",
        url="https://www.youtube.com/channel/UCakddO7wKR9RAdK0VYlJ4Vw",
        source_type=Source.SourceType.YOUTUBE_CHANNEL,
        description="Church history lectures",
        is_active=True,
    )


@pytest.fixture
def inactive_source(db):
    """Create an inactive source."""
    return Source.objects.create(
        name="Inactive Source",
        url="https://example.com",
        source_type=Source.SourceType.BLOG,
        is_active=False,
    )


@pytest.fixture
def content_item(db, source):
    """Create a test content item."""
    return ContentItem.objects.create(
        source=source,
        content_type=ContentItem.ContentType.TRANSCRIPT,
        title="Augustine's Confessions",
        url="https://www.youtube.com/watch?v=ABC123",
        external_id="ABC123",
        author="Ryan Reeves",
        published_date=date(2024, 1, 15),
        raw_text="This is a transcript about Augustine.",
        processed_text="This is a transcript about Augustine.",
        token_count=10,
        is_processed=True,
    )


@pytest.fixture
def content_tag(db):
    """Create a test content tag."""
    return ContentTag.objects.create(
        name="Early Church",
        tag_type=ContentTag.TagType.ERA,
        slug="early-church",
    )


@pytest.fixture
def authenticated_client(create_user):
    """Create an authenticated API client."""
    user = create_user()
    client = APIClient()
    refresh = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return client


# =============================================================================
# Model Tests
# =============================================================================


@pytest.mark.django_db
class TestSource:
    """Test Source model."""

    def test_create_source_with_all_fields(self):
        """Test creating a source with all fields."""
        source = Source.objects.create(
            name="Dr. Jordan Cooper",
            url="https://www.youtube.com/channel/UCexampleID",
            source_type=Source.SourceType.YOUTUBE_CHANNEL,
            description="Lutheran theology and church history",
            scrape_config={"playlist_id": "PLexample", "max_videos": 100},
            is_active=True,
        )

        assert source.name == "Dr. Jordan Cooper"
        assert source.url == "https://www.youtube.com/channel/UCexampleID"
        assert source.source_type == Source.SourceType.YOUTUBE_CHANNEL
        assert source.description == "Lutheran theology and church history"
        assert source.scrape_config == {"playlist_id": "PLexample", "max_videos": 100}
        assert source.is_active is True
        assert source.created_at is not None
        assert source.updated_at is not None

    def test_source_str_representation(self, source):
        """Test Source __str__ method."""
        assert str(source) == "Ryan Reeves (YouTube Channel)"

    def test_source_ordering(self, db):
        """Test Source default ordering by name."""
        Source.objects.create(
            name="Zulu History",
            url="https://example.com/z",
            source_type=Source.SourceType.BLOG,
        )
        Source.objects.create(
            name="Alpha Church",
            url="https://example.com/a",
            source_type=Source.SourceType.BLOG,
        )

        sources = list(Source.objects.all())
        assert sources[0].name == "Alpha Church"
        assert sources[1].name == "Zulu History"


@pytest.mark.django_db
class TestContentItem:
    """Test ContentItem model."""

    def test_create_content_item_linked_to_source(self, source):
        """Test creating ContentItem linked to a Source."""
        item = ContentItem.objects.create(
            source=source,
            content_type=ContentItem.ContentType.TRANSCRIPT,
            title="The Reformation",
            url="https://www.youtube.com/watch?v=XYZ789",
            external_id="XYZ789",
            raw_text="Transcript text here",
        )

        assert item.source == source
        assert item.content_type == ContentItem.ContentType.TRANSCRIPT
        assert item.title == "The Reformation"
        assert item.external_id == "XYZ789"
        assert item.is_processed is False

    def test_content_item_unique_together_constraint(self, source):
        """Test unique_together constraint on (source, external_id)."""
        ContentItem.objects.create(
            source=source,
            content_type=ContentItem.ContentType.TRANSCRIPT,
            title="First Item",
            external_id="SAME_ID",
            raw_text="Text 1",
        )

        with pytest.raises(IntegrityError):
            ContentItem.objects.create(
                source=source,
                content_type=ContentItem.ContentType.TRANSCRIPT,
                title="Second Item",
                external_id="SAME_ID",
                raw_text="Text 2",
            )

    def test_content_item_str_representation(self, content_item):
        """Test ContentItem __str__ method."""
        assert str(content_item) == "Augustine's Confessions (Transcript)"

    def test_content_item_ordering(self, source):
        """Test ContentItem default ordering by -created_at."""
        item1 = ContentItem.objects.create(
            source=source,
            content_type=ContentItem.ContentType.TRANSCRIPT,
            title="Older Item",
            raw_text="Old text",
        )
        item2 = ContentItem.objects.create(
            source=source,
            content_type=ContentItem.ContentType.TRANSCRIPT,
            title="Newer Item",
            raw_text="New text",
        )

        items = list(ContentItem.objects.all())
        assert items[0] == item2  # Newer first
        assert items[1] == item1


@pytest.mark.django_db
class TestContentTag:
    """Test ContentTag model."""

    def test_create_content_tag(self):
        """Test creating a ContentTag."""
        tag = ContentTag.objects.create(
            name="Medieval Period",
            tag_type=ContentTag.TagType.ERA,
            slug="medieval-period",
        )

        assert tag.name == "Medieval Period"
        assert tag.tag_type == ContentTag.TagType.ERA
        assert tag.slug == "medieval-period"

    def test_content_tag_unique_together_constraint(self):
        """Test unique_together constraint on (name, tag_type)."""
        ContentTag.objects.create(
            name="Augustine",
            tag_type=ContentTag.TagType.PERSON,
            slug="augustine-person",
        )

        with pytest.raises(IntegrityError):
            ContentTag.objects.create(
                name="Augustine",
                tag_type=ContentTag.TagType.PERSON,
                slug="augustine-duplicate",
            )

    def test_content_tag_same_name_different_type_allowed(self):
        """Test that same name with different tag_type is allowed."""
        tag1 = ContentTag.objects.create(
            name="Reformation",
            tag_type=ContentTag.TagType.ERA,
            slug="reformation-era",
        )
        tag2 = ContentTag.objects.create(
            name="Reformation",
            tag_type=ContentTag.TagType.TOPIC,
            slug="reformation-topic",
        )

        assert tag1.name == tag2.name
        assert tag1.tag_type != tag2.tag_type

    def test_content_tag_str_representation(self, content_tag):
        """Test ContentTag __str__ method."""
        assert str(content_tag) == "Early Church (Era)"

    def test_content_tag_ordering(self):
        """Test ContentTag ordering by tag_type then name."""
        ContentTag.objects.create(
            name="Zulu", tag_type=ContentTag.TagType.TOPIC, slug="zulu"
        )
        ContentTag.objects.create(
            name="Alpha", tag_type=ContentTag.TagType.ERA, slug="alpha"
        )
        ContentTag.objects.create(
            name="Beta", tag_type=ContentTag.TagType.ERA, slug="beta"
        )

        tags = list(ContentTag.objects.all())
        assert tags[0].name == "Alpha"  # ERA comes first
        assert tags[1].name == "Beta"
        assert tags[2].name == "Zulu"  # TOPIC comes second


@pytest.mark.django_db
class TestContentItemTag:
    """Test ContentItemTag through model."""

    def test_content_item_tag_confidence_default(self, content_item, content_tag):
        """Test ContentItemTag confidence field default value."""
        item_tag = ContentItemTag.objects.create(
            content_item=content_item,
            tag=content_tag,
        )

        assert item_tag.confidence == 1.0

    def test_content_item_tag_custom_confidence(self, content_item, content_tag):
        """Test setting custom confidence value."""
        item_tag = ContentItemTag.objects.create(
            content_item=content_item,
            tag=content_tag,
            confidence=0.75,
        )

        assert item_tag.confidence == 0.75

    def test_content_item_tag_str_representation(self, content_item, content_tag):
        """Test ContentItemTag __str__ method."""
        item_tag = ContentItemTag.objects.create(
            content_item=content_item,
            tag=content_tag,
        )

        assert str(item_tag) == "Augustine's Confessions - Early Church"


@pytest.mark.django_db
class TestContentChunk:
    """Test ContentChunk model."""

    def test_content_chunk_str_representation(self, content_item):
        """Test ContentChunk __str__ method."""
        chunk = ContentChunk.objects.create(
            content_item=content_item,
            chunk_text="This is chunk text",
            chunk_index=0,
            token_count=5,
            embedding=[0.1] * 384,
        )

        assert str(chunk) == "Augustine's Confessions - Chunk 0"

    def test_content_chunk_ordering(self, content_item):
        """Test ContentChunk ordering by content_item and chunk_index."""
        chunk2 = ContentChunk.objects.create(
            content_item=content_item,
            chunk_text="Second chunk",
            chunk_index=1,
            token_count=5,
            embedding=[0.2] * 384,
        )
        chunk1 = ContentChunk.objects.create(
            content_item=content_item,
            chunk_text="First chunk",
            chunk_index=0,
            token_count=5,
            embedding=[0.1] * 384,
        )

        chunks = list(ContentChunk.objects.all())
        assert chunks[0] == chunk1
        assert chunks[1] == chunk2


# =============================================================================
# Utility Function Tests
# =============================================================================


class TestChunkText:
    """Test chunk_text utility function."""

    def test_chunk_text_with_short_text(self):
        """Test chunk_text with text shorter than max_tokens."""
        text = "This is a short text."
        chunks = chunk_text(text, max_tokens=512, overlap=50)

        assert len(chunks) == 1
        assert chunks[0][0] == text
        assert isinstance(chunks[0][1], int)  # token count

    def test_chunk_text_with_long_text(self):
        """Test chunk_text with text requiring multiple chunks."""
        # Create text that will definitely exceed 50 tokens
        text = " ".join(["This is a sentence about church history."] * 20)
        chunks = chunk_text(text, max_tokens=50, overlap=10)

        assert len(chunks) > 1
        for chunk_text_val, token_count in chunks:
            assert isinstance(chunk_text_val, str)
            assert isinstance(token_count, int)
            assert token_count > 0

    def test_chunk_text_with_empty_text(self):
        """Test chunk_text with empty or whitespace-only text."""
        assert chunk_text("", max_tokens=512, overlap=50) == []
        assert chunk_text("   ", max_tokens=512, overlap=50) == []
        assert chunk_text("\n\n", max_tokens=512, overlap=50) == []

    def test_chunk_text_overlap_produces_overlapping_content(self):
        """Test that chunk_text with overlap produces overlapping chunks."""
        text = " ".join([f"Sentence {i} about church history." for i in range(20)])
        chunks = chunk_text(text, max_tokens=50, overlap=10)

        if len(chunks) > 1:
            # Check that there's some overlap between consecutive chunks
            for i in range(len(chunks) - 1):
                chunk1_text = chunks[i][0]
                chunk2_text = chunks[i + 1][0]
                # At least some words should appear in both chunks
                chunk1_words = set(chunk1_text.split())
                chunk2_words = set(chunk2_text.split())
                # There should be some common words due to overlap
                assert len(chunk1_words & chunk2_words) > 0


class TestCleanTranscript:
    """Test clean_transcript utility function."""

    def test_clean_transcript_removes_timestamps(self):
        """Test that clean_transcript removes timestamp formats."""
        text = "[00:05:30] This is a sentence. [00:10:15] Another sentence."
        cleaned = clean_transcript(text)
        assert "[00:05:30]" not in cleaned
        assert "[00:10:15]" not in cleaned
        assert "This is a sentence." in cleaned

    def test_clean_transcript_removes_brackets(self):
        """Test that clean_transcript removes [bracket] annotations."""
        text = "This is a sentence. [applause] Another sentence. [laughter]"
        cleaned = clean_transcript(text)
        assert "[applause]" not in cleaned
        assert "[laughter]" not in cleaned
        assert "This is a sentence." in cleaned

    def test_clean_transcript_fixes_smart_quotes(self):
        """Test that clean_transcript converts smart quotes to regular quotes."""
        text = "He said \u2018hello\u2019 and she said \u201cwelcome\u201d"
        cleaned = clean_transcript(text)
        assert "\u2018" not in cleaned
        assert "\u2019" not in cleaned
        assert "\u201c" not in cleaned
        assert "\u201d" not in cleaned
        assert "'" in cleaned
        assert '"' in cleaned

    def test_clean_transcript_handles_empty_text(self):
        """Test clean_transcript with empty string."""
        assert clean_transcript("") == ""
        assert clean_transcript("   ") == ""

    def test_clean_transcript_removes_music_annotations(self):
        """Test that clean_transcript removes music annotations."""
        text = "This is text. (background music) More text."
        cleaned = clean_transcript(text)
        assert "(background music)" not in cleaned
        assert "This is text." in cleaned

    def test_clean_transcript_normalizes_whitespace(self):
        """Test that clean_transcript fixes multiple spaces and newlines."""
        text = "This  is   text.\n\n\n\nNew paragraph."
        cleaned = clean_transcript(text)
        assert "  " not in cleaned  # No double spaces
        assert "\n\n\n" not in cleaned  # No triple newlines


class TestCountTokens:
    """Test count_tokens utility function."""

    def test_count_tokens_returns_integer(self):
        """Test that count_tokens returns an integer."""
        text = "This is a test sentence for token counting."
        token_count = count_tokens(text)
        assert isinstance(token_count, int)
        assert token_count > 0

    def test_count_tokens_empty_string(self):
        """Test count_tokens with empty string."""
        assert count_tokens("") == 0

    def test_count_tokens_longer_text_has_more_tokens(self):
        """Test that longer text has more tokens."""
        short_text = "Hello world."
        long_text = "This is a much longer text with many more words."
        assert count_tokens(long_text) > count_tokens(short_text)


# =============================================================================
# Serializer Tests
# =============================================================================


@pytest.mark.django_db
class TestSerializers:
    """Test serializers for content models."""

    def test_source_serializer_includes_all_fields(self, source):
        """Test that SourceSerializer includes all required fields."""
        from apps.content.serializers import SourceSerializer

        serializer = SourceSerializer(source)
        data = serializer.data

        assert "id" in data
        assert data["name"] == "Ryan Reeves"
        assert data["url"] == "https://www.youtube.com/channel/UCakddO7wKR9RAdK0VYlJ4Vw"
        assert data["source_type"] == "youtube_channel"
        assert data["description"] == "Church history lectures"
        assert data["is_active"] is True
        assert "created_at" in data
        assert "updated_at" in data

    def test_content_item_serializer_includes_nested_source_and_tags(
        self, content_item, content_tag
    ):
        """Test that ContentItemSerializer includes nested source and tags."""
        from apps.content.serializers import ContentItemSerializer

        content_item.tags.add(content_tag)
        serializer = ContentItemSerializer(content_item)
        data = serializer.data

        assert "source" in data
        assert data["source"]["name"] == "Ryan Reeves"
        assert "tags" in data
        assert len(data["tags"]) == 1
        assert data["tags"][0]["name"] == "Early Church"

    def test_content_chunk_serializer_includes_similarity_score_field(
        self, content_item
    ):
        """Test that ContentChunkSerializer includes similarity_score field."""
        from apps.content.serializers import ContentChunkSerializer

        chunk = ContentChunk.objects.create(
            content_item=content_item,
            chunk_text="Test chunk",
            chunk_index=0,
            token_count=5,
            embedding=[0.1] * 384,
        )
        chunk.similarity_score = 0.95  # Dynamically added field

        serializer = ContentChunkSerializer(chunk)
        data = serializer.data

        assert "similarity_score" in data
        assert data["similarity_score"] == 0.95

    def test_content_tag_serializer_output(self, content_tag):
        """Test ContentTagSerializer output."""
        from apps.content.serializers import ContentTagSerializer

        serializer = ContentTagSerializer(content_tag)
        data = serializer.data

        assert data["name"] == "Early Church"
        assert data["tag_type"] == "era"
        assert data["slug"] == "early-church"


# =============================================================================
# API Endpoint Tests
# =============================================================================


@pytest.mark.django_db
class TestSourceViewSet:
    """Test SourceViewSet API endpoints."""

    def test_get_sources_returns_active_sources_authenticated(
        self, authenticated_client, source, inactive_source
    ):
        """Test GET /api/content/sources/ returns only active sources."""
        response = authenticated_client.get("/api/content/sources/")

        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]["name"] == "Ryan Reeves"

    def test_get_sources_returns_401_unauthenticated(self, api_client, source):
        """Test GET /api/content/sources/ returns 401 without authentication."""
        response = api_client.get("/api/content/sources/")
        assert response.status_code == 401


@pytest.mark.django_db
class TestContentItemViewSet:
    """Test ContentItemViewSet API endpoints."""

    def test_get_content_items_returns_items(
        self, authenticated_client, content_item
    ):
        """Test GET /api/content/items/ returns content items."""
        response = authenticated_client.get("/api/content/items/")

        assert response.status_code == 200
        assert len(response.data) >= 1
        assert response.data[0]["title"] == "Augustine's Confessions"

    def test_get_content_items_filter_by_source(
        self, authenticated_client, source, content_item
    ):
        """Test GET /api/content/items/?source=1 filters by source."""
        # Create another source and item
        other_source = Source.objects.create(
            name="Other Source",
            url="https://example.com",
            source_type=Source.SourceType.BLOG,
        )
        other_item = ContentItem.objects.create(
            source=other_source,
            content_type=ContentItem.ContentType.ARTICLE,
            title="Other Article",
            raw_text="Other text",
        )

        response = authenticated_client.get(f"/api/content/items/?source={source.id}")

        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]["title"] == "Augustine's Confessions"

    def test_get_content_items_filter_by_content_type(
        self, authenticated_client, content_item
    ):
        """Test GET /api/content/items/?content_type=transcript filters by type."""
        # Create an article
        ContentItem.objects.create(
            source=content_item.source,
            content_type=ContentItem.ContentType.ARTICLE,
            title="An Article",
            raw_text="Article text",
        )

        response = authenticated_client.get(
            "/api/content/items/?content_type=transcript"
        )

        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]["content_type"] == "transcript"


@pytest.mark.django_db
class TestContentSearchEndpoint:
    """Test content_search API endpoint."""

    def test_post_search_returns_400_without_query(self, authenticated_client):
        """Test POST /api/content/search/ returns 400 without query."""
        response = authenticated_client.post("/api/content/search/", {})

        assert response.status_code == 400
        assert "error" in response.data
        assert "required" in response.data["error"].lower()

    def test_post_search_with_query_parameter(self, authenticated_client):
        """Test POST /api/content/search/ with query parameter."""
        # This test will skip embedding generation if sentence-transformers not installed
        response = authenticated_client.post(
            "/api/content/search/",
            {"query": "Augustine"},
        )

        # Accept either success (200) or service unavailable (503) if no embeddings
        assert response.status_code in [200, 503]
