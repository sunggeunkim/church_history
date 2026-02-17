"""Serializers for progress tracking API endpoints."""

from rest_framework import serializers

from apps.eras.models import Era


class MarkEraVisitedSerializer(serializers.Serializer):
    """Serializer for marking an era as visited."""

    era_id = serializers.IntegerField()

    def validate_era_id(self, value):
        """Validate that the era exists."""
        if not Era.objects.filter(id=value).exists():
            raise serializers.ValidationError("Era not found.")
        return value
