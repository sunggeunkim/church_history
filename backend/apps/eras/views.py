"""Views for eras API."""

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import Era
from .serializers import EraDetailSerializer, EraListSerializer


class EraViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for church history eras.

    Provides:
    - list: All eras with basic info for timeline
    - retrieve: Single era with key events and figures
    - timeline: Custom endpoint for timeline visualization

    Eras are public reference data accessible without authentication.
    """

    queryset = Era.objects.all().prefetch_related("key_events", "key_figures")
    permission_classes = [AllowAny]
    lookup_field = "slug"

    def get_serializer_class(self):
        """Use detail serializer for retrieve, list serializer for list."""
        if self.action == "retrieve":
            return EraDetailSerializer
        return EraListSerializer

    @method_decorator(cache_page(60 * 15))
    @action(detail=False, methods=["get"])
    def timeline(self, request):
        """Get all eras with their events for timeline visualization.

        Returns eras ordered by start year with key events included.
        Cached for 15 minutes since era data changes infrequently.
        """
        eras = self.get_queryset()
        serializer = EraDetailSerializer(eras, many=True)
        return Response(serializer.data)
