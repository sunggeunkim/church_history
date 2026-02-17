import pytest
from django.conf import settings


@pytest.mark.django_db
class TestHealthCheck:
    def test_health_check_returns_200(self, api_client):
        response = api_client.get("/api/health/")
        assert response.status_code == 200

    def test_health_check_response_body(self, api_client):
        response = api_client.get("/api/health/")
        data = response.json()
        assert data["status"] == "ok"
        assert data["version"] == "0.1.0"


class TestDjangoSettings:
    def test_secret_key_is_set(self):
        assert settings.SECRET_KEY is not None
        assert len(settings.SECRET_KEY) > 0

    def test_installed_apps_include_local_apps(self):
        assert "apps.accounts" in settings.INSTALLED_APPS
        assert "apps.content" in settings.INSTALLED_APPS
        assert "apps.eras" in settings.INSTALLED_APPS
        assert "apps.chat" in settings.INSTALLED_APPS
        assert "apps.quiz" in settings.INSTALLED_APPS
        assert "apps.progress" in settings.INSTALLED_APPS
        assert "apps.sharing" in settings.INSTALLED_APPS

    def test_rest_framework_configured(self):
        assert "rest_framework" in settings.INSTALLED_APPS
        assert "DEFAULT_AUTHENTICATION_CLASSES" in settings.REST_FRAMEWORK

    def test_auth_user_model(self):
        assert settings.AUTH_USER_MODEL == "accounts.User"

    def test_database_engine(self):
        engine = settings.DATABASES["default"]["ENGINE"]
        assert engine in (
            "django.db.backends.postgresql",
            "django.db.backends.sqlite3",
        )

    def test_app_version(self):
        assert settings.APP_VERSION == "0.1.0"
