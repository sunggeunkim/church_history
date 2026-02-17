import pytest
from django.test import RequestFactory
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    """Return an API client for making test requests."""
    return APIClient()


@pytest.fixture
def request_factory():
    """Return a Django RequestFactory instance."""
    return RequestFactory()


@pytest.fixture
def create_user(db):
    """Factory fixture to create test users."""
    from apps.accounts.models import User

    def _create_user(
        email="test@example.com",
        username="testuser",
        password="testpass123",
        **kwargs,
    ):
        return User.objects.create_user(
            email=email,
            username=username,
            password=password,
            **kwargs,
        )

    return _create_user
