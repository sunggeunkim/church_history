"""Views for eras API."""

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Era
from .serializers import EraDetailSerializer, EraListSerializer


class EraViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for church history eras.

    Provides:
    - list: All eras with basic info for timeline
    - retrieve: Single era with key events and figures
    - timeline: Custom endpoint for timeline visualization
    """

    queryset = Era.objects.all().prefetch_related("key_events", "key_figures")
    lookup_field = "slug"

    def get_serializer_class(self):
        """Use detail serializer for retrieve, list serializer for list."""
        if self.action == "retrieve":
            return EraDetailSerializer
        return EraListSerializer

    @action(detail=False, methods=["get"])
    def timeline(self, request):
        """Get all eras with their events for timeline visualization.

        Returns eras ordered by start year with key events included.
        """
        eras = self.get_queryset()
        serializer = EraDetailSerializer(eras, many=True)
        return Response(serializer.data)
