from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "username", "display_name", "avatar_url", "date_joined")
        read_only_fields = ("id", "date_joined")
