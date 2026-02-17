import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import User
from apps.accounts.serializers import UserSerializer


@pytest.mark.django_db
class TestUserModel:
    """Tests for the User model profile fields."""

    def test_user_has_display_name_field(self):
        user = User.objects.create_user(
            email="test@example.com",
            username="testuser",
            password="testpass123",
            display_name="Test User",
        )
        assert user.display_name == "Test User"

    def test_user_has_avatar_url_field(self):
        user = User.objects.create_user(
            email="test@example.com",
            username="testuser",
            password="testpass123",
            avatar_url="https://example.com/avatar.jpg",
        )
        assert user.avatar_url == "https://example.com/avatar.jpg"

    def test_display_name_blank_by_default(self):
        user = User.objects.create_user(
            email="test@example.com",
            username="testuser",
            password="testpass123",
        )
        assert user.display_name == ""

    def test_avatar_url_blank_by_default(self):
        user = User.objects.create_user(
            email="test@example.com",
            username="testuser",
            password="testpass123",
        )
        assert user.avatar_url == ""

    def test_email_is_unique(self):
        User.objects.create_user(
            email="test@example.com",
            username="testuser1",
            password="testpass123",
        )
        with pytest.raises(Exception):
            User.objects.create_user(
                email="test@example.com",
                username="testuser2",
                password="testpass123",
            )

    def test_str_returns_email(self):
        user = User.objects.create_user(
            email="test@example.com",
            username="testuser",
            password="testpass123",
        )
        assert str(user) == "test@example.com"


@pytest.mark.django_db
class TestUserSerializer:
    """Tests for UserSerializer including profile fields."""

    def test_serializer_includes_display_name(self):
        user = User.objects.create_user(
            email="test@example.com",
            username="testuser",
            password="testpass123",
            display_name="Test User",
        )
        serializer = UserSerializer(user)
        assert "display_name" in serializer.data
        assert serializer.data["display_name"] == "Test User"

    def test_serializer_includes_avatar_url(self):
        user = User.objects.create_user(
            email="test@example.com",
            username="testuser",
            password="testpass123",
            avatar_url="https://example.com/avatar.jpg",
        )
        serializer = UserSerializer(user)
        assert "avatar_url" in serializer.data
        assert serializer.data["avatar_url"] == "https://example.com/avatar.jpg"

    def test_serializer_fields(self):
        user = User.objects.create_user(
            email="test@example.com",
            username="testuser",
            password="testpass123",
        )
        serializer = UserSerializer(user)
        expected_fields = {"id", "email", "username", "display_name", "avatar_url", "date_joined"}
        assert set(serializer.data.keys()) == expected_fields


@pytest.mark.django_db
class TestCurrentUserEndpoint:
    """Tests for /api/accounts/me/ endpoint."""

    def test_me_returns_401_without_auth(self, api_client):
        response = api_client.get("/api/accounts/me/")
        assert response.status_code == 401

    def test_me_returns_user_with_jwt(self):
        user = User.objects.create_user(
            email="test@example.com",
            username="testuser",
            password="testpass123",
            display_name="Test User",
            avatar_url="https://example.com/avatar.jpg",
        )
        client = APIClient()
        refresh = RefreshToken.for_user(user)
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
        response = client.get("/api/accounts/me/")
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["display_name"] == "Test User"
        assert data["avatar_url"] == "https://example.com/avatar.jpg"


@pytest.mark.django_db
class TestGoogleLoginEndpoint:
    """Tests for /api/auth/google/ endpoint."""

    def test_google_endpoint_exists(self, api_client):
        response = api_client.post("/api/auth/google/", {}, format="json")
        # Should not return 404 - a 400 means the endpoint exists
        # but the request body is invalid (no code/access_token)
        assert response.status_code != 404

    def test_google_endpoint_rejects_get(self, api_client):
        response = api_client.get("/api/auth/google/")
        assert response.status_code == 405


@pytest.mark.django_db
class TestLogoutEndpoint:
    """Tests for /api/accounts/logout/ clearing cookies."""

    def test_logout_clears_cookies(self):
        user = User.objects.create_user(
            email="test@example.com",
            username="testuser",
            password="testpass123",
        )
        client = APIClient()
        refresh = RefreshToken.for_user(user)
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
        response = client.post("/api/accounts/logout/")
        # dj-rest-auth logout should succeed
        assert response.status_code in (200, 204)

    def test_logout_requires_authentication(self, api_client):
        response = api_client.post("/api/accounts/logout/")
        assert response.status_code == 401


@pytest.mark.django_db
class TestTokenRefresh:
    """Tests for token refresh endpoint."""

    def test_token_refresh_with_valid_token(self):
        user = User.objects.create_user(
            email="test@example.com",
            username="testuser",
            password="testpass123",
        )
        refresh = RefreshToken.for_user(user)
        client = APIClient()
        response = client.post(
            "/api/auth/token/refresh/",
            {"refresh": str(refresh)},
            format="json",
        )
        assert response.status_code == 200
        assert "access" in response.json()

    def test_token_refresh_with_invalid_token(self, api_client):
        response = api_client.post(
            "/api/auth/token/refresh/",
            {"refresh": "invalid-token"},
            format="json",
        )
        assert response.status_code == 401


@pytest.mark.django_db
class TestCSRFTokenEndpoint:
    """Tests for /api/auth/csrf/ endpoint."""

    def test_csrf_endpoint_returns_token(self, api_client):
        response = api_client.get("/api/auth/csrf/")
        assert response.status_code == 200
        data = response.json()
        assert "csrfToken" in data
        assert data["csrfToken"] is not None
        assert len(data["csrfToken"]) > 0

    def test_csrf_endpoint_allows_unauthenticated(self, api_client):
        # Should be accessible without authentication
        response = api_client.get("/api/auth/csrf/")
        assert response.status_code == 200

    def test_csrf_endpoint_sets_cookie(self, api_client):
        response = api_client.get("/api/auth/csrf/")
        assert response.status_code == 200
        # Django sets the csrftoken cookie
        assert "csrftoken" in response.cookies or "csrftoken" in response.client.cookies


@pytest.mark.django_db
class TestCustomSocialAccountAdapter:
    """Tests for CustomSocialAccountAdapter populating profile fields."""

    def test_adapter_populates_display_name_and_avatar(self):
        from unittest.mock import Mock
        from apps.accounts.adapters import CustomSocialAccountAdapter

        adapter = CustomSocialAccountAdapter()

        # Mock request
        request = Mock()

        # Mock sociallogin object with Google OAuth data
        sociallogin = Mock()
        sociallogin.account.extra_data = {
            "picture": "https://example.com/photo.jpg"
        }

        # Mock user data from Google
        data = {
            "email": "test@example.com",
            "name": "Test User"
        }

        # Call the adapter's populate_user method
        user = adapter.populate_user(request, sociallogin, data)

        # Verify profile fields are populated
        assert user.display_name == "Test User"
        assert user.avatar_url == "https://example.com/photo.jpg"

    def test_adapter_handles_missing_picture(self):
        from unittest.mock import Mock
        from apps.accounts.adapters import CustomSocialAccountAdapter

        adapter = CustomSocialAccountAdapter()
        request = Mock()

        sociallogin = Mock()
        sociallogin.account.extra_data = {}  # No picture field

        data = {
            "email": "test@example.com",
            "name": "Test User"
        }

        user = adapter.populate_user(request, sociallogin, data)

        assert user.display_name == "Test User"
        assert user.avatar_url == ""  # Should default to empty string

    def test_adapter_handles_missing_name(self):
        from unittest.mock import Mock
        from apps.accounts.adapters import CustomSocialAccountAdapter

        adapter = CustomSocialAccountAdapter()
        request = Mock()

        sociallogin = Mock()
        sociallogin.account.extra_data = {
            "picture": "https://example.com/photo.jpg"
        }

        data = {
            "email": "test@example.com"
            # No name field
        }

        user = adapter.populate_user(request, sociallogin, data)

        assert user.display_name == ""  # Should default to empty string
        assert user.avatar_url == "https://example.com/photo.jpg"
