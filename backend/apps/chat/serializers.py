"""Serializers for chat app API endpoints."""

from rest_framework import serializers

from .models import ChatMessage, ChatSession, MessageCitation


class MessageCitationSerializer(serializers.ModelSerializer):
    """Serializer for MessageCitation model."""

    class Meta:
        model = MessageCitation
        fields = [
            "id",
            "title",
            "url",
            "source_name",
            "order",
        ]
        read_only_fields = ["id"]


class ChatMessageSerializer(serializers.ModelSerializer):
    """Serializer for ChatMessage model with nested citations."""

    citations = MessageCitationSerializer(many=True, read_only=True)

    class Meta:
        model = ChatMessage
        fields = [
            "id",
            "session",
            "role",
            "content",
            "created_at",
            "model_used",
            "input_tokens",
            "output_tokens",
            "citations",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "model_used",
            "input_tokens",
            "output_tokens",
        ]


class ChatSessionSerializer(serializers.ModelSerializer):
    """Serializer for ChatSession model with annotated message count."""

    message_count = serializers.IntegerField(read_only=True, default=0)
    era_name = serializers.CharField(source="era.name", read_only=True, default=None)

    class Meta:
        model = ChatSession
        fields = [
            "id",
            "title",
            "era",
            "era_name",
            "created_at",
            "updated_at",
            "is_archived",
            "total_input_tokens",
            "total_output_tokens",
            "message_count",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "total_input_tokens",
            "total_output_tokens",
        ]


class ChatSessionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new ChatSession."""

    class Meta:
        model = ChatSession
        fields = ["id", "title", "era"]
        read_only_fields = ["id"]


class ChatStreamSerializer(serializers.Serializer):
    """Serializer for validating chat stream request data."""

    session_id = serializers.IntegerField()
    message = serializers.CharField(max_length=10000)
