from rest_framework import generics, permissions

from .serializers import UserSerializer


class CurrentUserView(generics.RetrieveAPIView):
    """Retrieve the currently authenticated user."""

    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
