from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from decouple import config
from dj_rest_auth.registration.views import SocialLoginView
from dj_rest_auth.views import LogoutView as DjRestAuthLogoutView
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import UserSerializer


class CurrentUserView(generics.RetrieveAPIView):
    """Retrieve the currently authenticated user."""

    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class GoogleLoginView(SocialLoginView):
    """Handle Google OAuth2 login via authorization code or access token.

    Frontend sends a POST with {"code": "..."} or {"access_token": "..."}
    and this view verifies with Google and returns JWT tokens as httpOnly cookies.
    """

    adapter_class = GoogleOAuth2Adapter
    # Must be "postmessage" for @react-oauth/google popup flow.
    # Google Identity Services sets redirect_uri=postmessage for auth-code popup.
    callback_url = config("GOOGLE_CALLBACK_URL", default="postmessage")
    client_class = OAuth2Client


class LogoutView(DjRestAuthLogoutView):
    """Log out the current user and clear JWT cookies.

    Requires authentication. Clears the toledot_access and toledot_refresh
    httpOnly cookies and returns a success message.
    """

    permission_classes = [permissions.IsAuthenticated]


class CSRFTokenView(APIView):
    """Return a CSRF token for the SPA.

    This endpoint is needed because httpOnly cookies require CSRF protection.
    The CSRF cookie is set automatically by Django's middleware.
    """

    permission_classes = [permissions.AllowAny]

    def get(self, request):
        from django.middleware.csrf import get_token

        csrf_token = get_token(request)
        return Response({"csrfToken": csrf_token})
