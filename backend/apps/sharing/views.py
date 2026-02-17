"""Views for social sharing."""

import logging

from django.conf import settings
from django.db.models import F
from django.shortcuts import get_object_or_404, render
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import ShareLink
from .serializers import CreateShareLinkSerializer, ShareLinkSerializer
from .services import build_content_snapshot
from .throttles import SharingBurstThrottle, SharingRateThrottle

logger = logging.getLogger(__name__)


class CreateShareLinkView(GenericAPIView):
    """Create a new share link.

    Endpoint: POST /api/sharing/links/
    """

    permission_classes = [IsAuthenticated]
    serializer_class = CreateShareLinkSerializer
    throttle_classes = [SharingRateThrottle, SharingBurstThrottle]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        share_type = serializer.validated_data["share_type"]
        content_snapshot = build_content_snapshot(
            user=request.user,
            share_type=share_type,
            achievement_id=serializer.validated_data.get("achievement_id"),
            quiz_id=serializer.validated_data.get("quiz_id"),
        )

        share_link = ShareLink.objects.create(
            user=request.user,
            share_type=share_type,
            content_snapshot=content_snapshot,
            sharer_display_name=request.user.display_name or request.user.email,
        )

        return Response(
            ShareLinkSerializer(share_link).data,
            status=status.HTTP_201_CREATED,
        )


class ListShareLinksView(GenericAPIView):
    """List the authenticated user's share links.

    Endpoint: GET /api/sharing/links/list/
    """

    permission_classes = [IsAuthenticated]
    serializer_class = ShareLinkSerializer

    def get(self, request):
        links = ShareLink.objects.filter(
            user=request.user,
            is_active=True,
        ).order_by("-created_at")

        serializer = self.get_serializer(links, many=True)
        return Response({"count": links.count(), "results": serializer.data})


class DeleteShareLinkView(GenericAPIView):
    """Deactivate a share link.

    Endpoint: DELETE /api/sharing/links/{token}/
    """

    permission_classes = [IsAuthenticated]

    def delete(self, request, token):
        share_link = get_object_or_404(
            ShareLink,
            token=token,
            user=request.user,
            is_active=True,
        )
        share_link.is_active = False
        share_link.save(update_fields=["is_active"])
        return Response(status=status.HTTP_204_NO_CONTENT)


def public_share_page(request, token):
    """Render the public share page (Django template).

    This is NOT an API endpoint. It serves an HTML page with:
    - Open Graph meta tags for social media previews
    - A styled share card displaying the shared content
    - A call-to-action linking back to the app

    No authentication required.
    """
    share_link = get_object_or_404(ShareLink, token=token, is_active=True)

    # Increment view count atomically
    ShareLink.objects.filter(pk=share_link.pk).update(view_count=F("view_count") + 1)

    # Build OG meta data
    og_data = _build_og_data(share_link)

    context = {
        "share_link": share_link,
        "og": og_data,
        "app_url": getattr(settings, "FRONTEND_URL", "http://localhost:5173"),
    }

    return render(request, "sharing/public_share.html", context)


def _build_og_data(share_link):
    """Build Open Graph meta tag data from a share link."""
    snapshot = share_link.content_snapshot
    sharer = share_link.sharer_display_name

    if share_link.share_type == ShareLink.ShareType.ACHIEVEMENT:
        return {
            "title": f'{sharer} unlocked "{snapshot["achievement_name"]}" on Toledot',
            "description": snapshot["achievement_description"],
            "type": "website",
        }
    elif share_link.share_type == ShareLink.ShareType.QUIZ_RESULT:
        era = snapshot.get("era_name", "All Eras")
        score = snapshot["percentage_score"]
        passed = "Passed" if snapshot["passed"] else "Attempted"
        return {
            "title": f"{sharer} scored {score}% on a {era} quiz -- Toledot",
            "description": (
                f"{passed} a {snapshot['difficulty']} quiz on {era} church history "
                f"with a score of {snapshot['score']}/{snapshot['total_questions']}."
            ),
            "type": "website",
        }
    elif share_link.share_type == ShareLink.ShareType.PROGRESS:
        pct = snapshot["completion_percentage"]
        return {
            "title": f"{sharer}'s Learning Journey -- {pct}% Complete -- Toledot",
            "description": (
                f"{sharer} has explored {snapshot['eras_visited']} eras, "
                f"passed {snapshot['quizzes_passed']} quizzes, and unlocked "
                f"{snapshot['achievements_unlocked']} achievements on Toledot."
            ),
            "type": "website",
        }

    return {
        "title": "Shared on Toledot",
        "description": "Explore church history with Toledot.",
        "type": "website",
    }
