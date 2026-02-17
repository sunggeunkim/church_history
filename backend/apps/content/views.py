"""API views for content app."""

from django.db.models import F
from pgvector.django import CosineDistance
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import ContentChunk, ContentItem, Source
from .serializers import (
    ContentChunkSerializer,
    ContentItemSerializer,
    SourceSerializer,
)


class SourceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for listing and retrieving content sources.

    Endpoints:
    - GET /api/content/sources/ - List all active sources
    - GET /api/content/sources/{id}/ - Retrieve a specific source
    """

    queryset = Source.objects.filter(is_active=True)
    serializer_class = SourceSerializer
    permission_classes = [IsAuthenticated]


class ContentItemViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for listing and retrieving content items.

    Endpoints:
    - GET /api/content/items/ - List all content items
    - GET /api/content/items/{id}/ - Retrieve a specific content item

    Filters:
    - source: Filter by source ID
    - content_type: Filter by content type (transcript, article, etc.)
    - tag: Filter by tag ID
    - is_processed: Filter by processing status
    """

    queryset = ContentItem.objects.select_related("source").prefetch_related("tags")
    serializer_class = ContentItemSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["source", "content_type", "is_processed"]

    def get_queryset(self):
        """Apply additional filters based on query parameters."""
        queryset = super().get_queryset()

        # Filter by tag
        tag_id = self.request.query_params.get("tag")
        if tag_id:
            queryset = queryset.filter(tags__id=tag_id)

        # Filter by source type
        source_type = self.request.query_params.get("source_type")
        if source_type:
            queryset = queryset.filter(source__source_type=source_type)

        return queryset.distinct()


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def content_search(request):
    """
    Semantic search endpoint using vector similarity.

    POST /api/content/search/
    Body:
    {
        "query": "text to search for",
        "top_k": 5,  // optional, default 5
        "min_score": 0.5  // optional, minimum similarity score (0.0-1.0)
    }

    Returns:
    List of ContentChunk objects with similarity scores, ordered by relevance.

    Note: This endpoint requires query embeddings to be generated on the client side
    or by a separate service. For MVP, you'll need to integrate with sentence-transformers
    to generate embeddings from the query text.
    """
    query_text = request.data.get("query")
    top_k = request.data.get("top_k", 5)
    min_score = request.data.get("min_score", 0.0)

    if not query_text:
        return Response(
            {"error": "Query text is required"}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Generate embedding from query text server-side
        query_embedding = _get_query_embedding(query_text)

        # Perform vector similarity search using cosine distance
        chunks = (
            ContentChunk.objects.select_related("content_item__source")
            .prefetch_related("content_item__tags")
            .annotate(
                distance=CosineDistance("embedding", query_embedding),
            )
            .order_by("distance")[:top_k]
        )

        # Filter by minimum similarity score (1 - cosine distance)
        results = []
        for chunk in chunks:
            similarity = 1 - chunk.distance
            if similarity >= min_score:
                chunk.similarity_score = similarity
                results.append(chunk)

        serializer = ContentChunkSerializer(results, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except ImportError:
        return Response(
            {"error": "sentence-transformers is not installed on the server."},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
    except Exception as e:
        return Response(
            {"error": f"Search failed: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


# Lazy-loaded embedding model singleton
_embedding_model = None


def _get_query_embedding(text: str):
    """Generate embedding for a query using sentence-transformers."""
    global _embedding_model
    if _embedding_model is None:
        from sentence_transformers import SentenceTransformer

        _embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    return _embedding_model.encode(text).tolist()
