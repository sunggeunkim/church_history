"""Serializers for social sharing."""

from rest_framework import serializers

from .models import ShareLink


class CreateShareLinkSerializer(serializers.Serializer):
    """Serializer for creating a new share link."""

    share_type = serializers.ChoiceField(choices=ShareLink.ShareType.choices)
    achievement_id = serializers.IntegerField(required=False)
    quiz_id = serializers.IntegerField(required=False)

    def validate(self, attrs):
        share_type = attrs["share_type"]
        if share_type == "achievement" and "achievement_id" not in attrs:
            raise serializers.ValidationError(
                {"achievement_id": "Required when share_type is 'achievement'."}
            )
        if share_type == "quiz_result" and "quiz_id" not in attrs:
            raise serializers.ValidationError(
                {"quiz_id": "Required when share_type is 'quiz_result'."}
            )
        return attrs


class ShareLinkSerializer(serializers.ModelSerializer):
    """Serializer for ShareLink model (read)."""

    share_url = serializers.CharField(read_only=True)

    class Meta:
        model = ShareLink
        fields = [
            "token",
            "share_type",
            "share_url",
            "content_snapshot",
            "sharer_display_name",
            "view_count",
            "is_active",
            "created_at",
        ]
        read_only_fields = fields
