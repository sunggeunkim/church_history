"""URL configuration for church_history project."""

from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from apps.accounts.views import CSRFTokenView, GoogleLoginView


@api_view(["GET"])
@permission_classes([AllowAny])
def health_check(request):
    """Health check endpoint."""
    return Response({"status": "ok", "version": settings.APP_VERSION})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", health_check, name="health-check"),
    path("api/accounts/", include("apps.accounts.urls")),
    path("api/content/", include("apps.content.urls")),
    path("api/eras/", include("apps.eras.urls")),
    path("api/chat/", include("apps.chat.urls")),
    path("api/quiz/", include("apps.quiz.urls")),
    path("api/progress/", include("apps.progress.urls")),
    path("api/sharing/", include("apps.sharing.urls")),
    path("accounts/", include("allauth.urls")),
    path("api/auth/", include("dj_rest_auth.urls")),
    path("api/auth/registration/", include("dj_rest_auth.registration.urls")),
    path("api/auth/csrf/", CSRFTokenView.as_view(), name="csrf-token"),
    path("api/auth/google/", GoogleLoginView.as_view(), name="google-login"),
    path(
        "api/auth/token/",
        TokenObtainPairView.as_view(),
        name="token-obtain-pair",
    ),
    path(
        "api/auth/token/refresh/",
        TokenRefreshView.as_view(),
        name="token-refresh",
    ),
]

if settings.DEBUG:
    urlpatterns += [
        path("__debug__/", include("debug_toolbar.urls")),
    ]
