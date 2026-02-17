"""Serializers for content app API endpoints."""

from rest_framework import serializers

from .models import ContentChunk, ContentItem, ContentTag, Source


class SourceSerializer(serializers.ModelSerializer):
    """Serializer for Source model."""

    class Meta:
        model = Source
        fields = [
            "id",
            "name",
            "url",
            "source_type",
            "description",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class ContentTagSerializer(serializers.ModelSerializer):
    """Serializer for ContentTag model."""

    class Meta:
        model = ContentTag
        fields = ["id", "name", "tag_type", "slug"]


class ContentItemSerializer(serializers.ModelSerializer):
    """Serializer for ContentItem model with nested tags."""

    source = SourceSerializer(read_only=True)
    tags = ContentTagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=ContentTag.objects.all(),
        write_only=True,
        required=False,
        source="tags",
    )

    class Meta:
        model = ContentItem
        fields = [
            "id",
            "source",
            "content_type",
            "title",
            "url",
            "external_id",
            "author",
            "published_date",
            "raw_text",
            "processed_text",
            "metadata",
            "is_processed",
            "token_count",
            "created_at",
            "updated_at",
            "tags",
            "tag_ids",
        ]
        read_only_fields = ["created_at", "updated_at"]


class ContentChunkSerializer(serializers.ModelSerializer):
    """Serializer for ContentChunk model, used for search results."""

    content_item = ContentItemSerializer(read_only=True)
    similarity_score = serializers.FloatField(read_only=True, required=False)

    class Meta:
        model = ContentChunk
        fields = [
            "id",
            "content_item",
            "chunk_text",
            "chunk_index",
            "token_count",
            "metadata",
            "created_at",
            "similarity_score",
        ]
        read_only_fields = ["created_at"]
