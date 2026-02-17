"""Content models for scraped content and embeddings.

This module defines models for storing scraped content from various sources
(YouTube channels, blogs, websites, books) and their vector embeddings for RAG.
"""

from django.db import models
from pgvector.django import VectorField, HnswIndex


class Source(models.Model):
    """A content source (YouTube channel, blog, website)."""

    class SourceType(models.TextChoices):
        YOUTUBE_CHANNEL = "youtube_channel", "YouTube Channel"
        YOUTUBE_PLAYLIST = "youtube_playlist", "YouTube Playlist"
        BLOG = "blog", "Blog"
        WEBSITE = "website", "Website"
        BOOK = "book", "Book"

    name = models.CharField(max_length=255)
    url = models.URLField(max_length=500)
    source_type = models.CharField(max_length=30, choices=SourceType.choices)
    description = models.TextField(blank=True)
    scrape_config = models.JSONField(
        default=dict, blank=True, help_text="Source-specific configuration"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.get_source_type_display()})"


class ContentTag(models.Model):
    """Tags for categorizing content (era, topic, tradition)."""

    class TagType(models.TextChoices):
        ERA = "era", "Era"
        TOPIC = "topic", "Topic"
        TRADITION = "tradition", "Tradition"
        PERSON = "person", "Person"

    name = models.CharField(max_length=100)
    tag_type = models.CharField(max_length=20, choices=TagType.choices)
    slug = models.SlugField(max_length=100)

    class Meta:
        unique_together = [["name", "tag_type"]]
        ordering = ["tag_type", "name"]

    def __str__(self):
        return f"{self.name} ({self.get_tag_type_display()})"


class ContentItem(models.Model):
    """A single piece of content (video transcript, article, book chapter)."""

    class ContentType(models.TextChoices):
        TRANSCRIPT = "transcript", "Transcript"
        ARTICLE = "article", "Article"
        BOOK_CHAPTER = "book_chapter", "Book Chapter"
        LECTURE_NOTES = "lecture_notes", "Lecture Notes"

    source = models.ForeignKey(Source, on_delete=models.CASCADE, related_name="items")
    content_type = models.CharField(max_length=30, choices=ContentType.choices)
    title = models.CharField(max_length=500)
    url = models.URLField(max_length=500, blank=True)
    external_id = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
        help_text="External identifier (e.g., YouTube video ID)",
    )
    author = models.CharField(max_length=255, blank=True)
    published_date = models.DateField(null=True, blank=True)
    raw_text = models.TextField()
    processed_text = models.TextField(
        blank=True, help_text="Cleaned and normalized text"
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional metadata (duration, views, etc.)",
    )
    is_processed = models.BooleanField(
        default=False, help_text="Whether chunks have been generated"
    )
    token_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tags = models.ManyToManyField(ContentTag, through="ContentItemTag", blank=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = [["source", "external_id"]]
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["source", "content_type"]),
        ]

    def __str__(self):
        return f"{self.title} ({self.get_content_type_display()})"


class ContentItemTag(models.Model):
    """Through table for M2M between ContentItem and ContentTag."""

    content_item = models.ForeignKey(ContentItem, on_delete=models.CASCADE)
    tag = models.ForeignKey(ContentTag, on_delete=models.CASCADE)
    confidence = models.FloatField(
        default=1.0, help_text="Confidence score for auto-tagged content (0.0-1.0)"
    )

    class Meta:
        unique_together = [["content_item", "tag"]]

    def __str__(self):
        return f"{self.content_item.title} - {self.tag.name}"


class ContentChunk(models.Model):
    """A chunk of content with its vector embedding for RAG."""

    content_item = models.ForeignKey(
        ContentItem, on_delete=models.CASCADE, related_name="chunks"
    )
    chunk_text = models.TextField()
    chunk_index = models.PositiveIntegerField()
    token_count = models.PositiveIntegerField(default=0)
    embedding = VectorField(dimensions=384)  # all-MiniLM-L6-v2 = 384d
    metadata = models.JSONField(
        default=dict, blank=True, help_text="Chunk-level metadata"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["content_item", "chunk_index"]
        indexes = [
            HnswIndex(
                name="chunk_embedding_hnsw_idx",
                fields=["embedding"],
                m=16,
                ef_construction=64,
                opclasses=["vector_cosine_ops"],
            ),
        ]

    def __str__(self):
        return f"{self.content_item.title} - Chunk {self.chunk_index}"
