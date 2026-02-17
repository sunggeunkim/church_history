"""Serializers for era models."""

from rest_framework import serializers

from .models import Era, KeyEvent, KeyFigure


class KeyEventSerializer(serializers.ModelSerializer):
    """Serializer for key events."""

    class Meta:
        model = KeyEvent
        fields = ["id", "year", "title", "description", "order"]


class KeyFigureSerializer(serializers.ModelSerializer):
    """Serializer for key figures."""

    class Meta:
        model = KeyFigure
        fields = [
            "id",
            "name",
            "birth_year",
            "death_year",
            "title",
            "description",
            "order",
        ]


class EraListSerializer(serializers.ModelSerializer):
    """Serializer for listing eras in timeline view."""

    class Meta:
        model = Era
        fields = [
            "id",
            "name",
            "slug",
            "start_year",
            "end_year",
            "color",
            "summary",
            "order",
        ]


class EraDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for era with related events and figures."""

    key_events = KeyEventSerializer(many=True, read_only=True)
    key_figures = KeyFigureSerializer(many=True, read_only=True)

    class Meta:
        model = Era
        fields = [
            "id",
            "name",
            "slug",
            "start_year",
            "end_year",
            "description",
            "summary",
            "color",
            "order",
            "image_url",
            "created_at",
            "key_events",
            "key_figures",
        ]
