"""Tests for social sharing functionality.

Tests models, services, serializers, views, and the public share page.
"""

import pytest
from django.utils import timezone
from rest_framework import status

from apps.eras.models import Era
from apps.progress.models import Achievement, UserAchievement, UserProgress
from apps.quiz.models import Quiz
from apps.chat.models import ChatSession
from apps.sharing.models import ShareLink, generate_share_token
from apps.sharing.services import build_content_snapshot


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def era(db):
    """Create a test era."""
    return Era.objects.create(
        name="Early Church",
        slug="early-church",
        start_year=33,
        end_year=325,
        description="The early church period",
        color="#C2410C",
        order=1,
    )


@pytest.fixture
def user(django_user_model):
    """Create a test user."""
    return django_user_model.objects.create_user(
        email="sharer@example.com",
        username="sharer",
        password="testpass123",
        display_name="Test Sharer",
    )


@pytest.fixture
def other_user(django_user_model):
    """Create another test user."""
    return django_user_model.objects.create_user(
        email="other@example.com",
        username="otheruser",
        password="testpass123",
        display_name="Other User",
    )


@pytest.fixture
def achievement(db):
    """Create a test achievement."""
    return Achievement.objects.create(
        slug="perfect-score",
        name="Perfect Scholar",
        description="Score 100% on any quiz",
        category=Achievement.Category.QUIZ,
        icon_key="star",
        order=1,
    )


@pytest.fixture
def user_achievement(user, achievement):
    """Create a user achievement (unlock)."""
    return UserAchievement.objects.create(
        user=user,
        achievement=achievement,
    )


@pytest.fixture
def completed_quiz(user, era):
    """Create a completed quiz."""
    return Quiz.objects.create(
        user=user,
        era=era,
        difficulty=Quiz.Difficulty.INTERMEDIATE,
        score=9,
        total_questions=10,
        completed_at=timezone.now(),
    )


@pytest.fixture
def share_link(user):
    """Create a test share link."""
    return ShareLink.objects.create(
        user=user,
        share_type=ShareLink.ShareType.ACHIEVEMENT,
        content_snapshot={
            "achievement_slug": "perfect-score",
            "achievement_name": "Perfect Scholar",
            "achievement_description": "Score 100% on any quiz",
            "achievement_category": "quiz",
            "achievement_icon_key": "star",
            "unlocked_at": "2026-02-17T10:30:00+00:00",
        },
        sharer_display_name="Test Sharer",
    )


# ---------------------------------------------------------------------------
# Model tests
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestShareLinkModel:
    """Tests for ShareLink model."""

    def test_create_share_link(self, user):
        """Test creating a ShareLink generates a token."""
        link = ShareLink.objects.create(
            user=user,
            share_type=ShareLink.ShareType.ACHIEVEMENT,
            content_snapshot={"test": "data"},
            sharer_display_name="Test User",
        )
        assert link.token
        assert len(link.token) == 8
        assert link.is_active is True
        assert link.view_count == 0

    def test_token_auto_generation(self, user):
        """Test that token is auto-generated on save when empty."""
        link = ShareLink(
            user=user,
            share_type=ShareLink.ShareType.QUIZ_RESULT,
            content_snapshot={"test": "data"},
            sharer_display_name="Test",
        )
        link.save()
        assert link.token
        assert len(link.token) == 8

    def test_token_uniqueness(self, user):
        """Test that multiple share links get unique tokens."""
        link1 = ShareLink.objects.create(
            user=user,
            share_type=ShareLink.ShareType.ACHIEVEMENT,
            content_snapshot={"test": "1"},
            sharer_display_name="Test",
        )
        link2 = ShareLink.objects.create(
            user=user,
            share_type=ShareLink.ShareType.ACHIEVEMENT,
            content_snapshot={"test": "2"},
            sharer_display_name="Test",
        )
        assert link1.token != link2.token

    def test_share_url_property(self, share_link):
        """Test share_url property returns correct URL."""
        assert share_link.share_url == f"http://localhost:8000/share/{share_link.token}"

    def test_str_representation(self, share_link):
        """Test string representation."""
        result = str(share_link)
        assert "Test Sharer" in result
        assert "Achievement" in result
        assert share_link.token in result

    def test_ordering(self, user):
        """Test that share links are ordered by -created_at."""
        link1 = ShareLink.objects.create(
            user=user,
            share_type=ShareLink.ShareType.ACHIEVEMENT,
            content_snapshot={"n": 1},
            sharer_display_name="Test",
        )
        link2 = ShareLink.objects.create(
            user=user,
            share_type=ShareLink.ShareType.PROGRESS,
            content_snapshot={"n": 2},
            sharer_display_name="Test",
        )
        links = list(ShareLink.objects.all())
        assert links[0].pk == link2.pk
        assert links[1].pk == link1.pk


@pytest.mark.django_db
class TestGenerateShareToken:
    """Tests for generate_share_token function."""

    def test_token_length(self):
        """Test default token length is 8."""
        token = generate_share_token()
        assert len(token) == 8

    def test_custom_length(self):
        """Test custom token length."""
        token = generate_share_token(length=12)
        assert len(token) == 12

    def test_token_is_alphanumeric(self):
        """Test token contains only alphanumeric characters."""
        token = generate_share_token()
        assert token.isalnum()

    def test_tokens_are_unique(self):
        """Test that generated tokens are unique (statistical)."""
        tokens = {generate_share_token() for _ in range(100)}
        assert len(tokens) == 100


# ---------------------------------------------------------------------------
# Service tests
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestBuildContentSnapshot:
    """Tests for build_content_snapshot service."""

    def test_build_achievement_snapshot(self, user, achievement, user_achievement):
        """Test building an achievement snapshot."""
        snapshot = build_content_snapshot(
            user=user,
            share_type="achievement",
            achievement_id=achievement.id,
        )
        assert snapshot["achievement_slug"] == "perfect-score"
        assert snapshot["achievement_name"] == "Perfect Scholar"
        assert snapshot["achievement_description"] == "Score 100% on any quiz"
        assert snapshot["achievement_category"] == "quiz"
        assert snapshot["achievement_icon_key"] == "star"
        assert "unlocked_at" in snapshot

    def test_build_achievement_snapshot_not_found(self, user):
        """Test 404 when achievement not found."""
        from django.http import Http404

        with pytest.raises(Http404):
            build_content_snapshot(
                user=user,
                share_type="achievement",
                achievement_id=9999,
            )

    def test_build_achievement_snapshot_not_unlocked(self, user, achievement):
        """Test 404 when user has not unlocked the achievement."""
        from django.http import Http404

        with pytest.raises(Http404):
            build_content_snapshot(
                user=user,
                share_type="achievement",
                achievement_id=achievement.id,
            )

    def test_build_quiz_snapshot(self, user, completed_quiz):
        """Test building a quiz result snapshot."""
        snapshot = build_content_snapshot(
            user=user,
            share_type="quiz_result",
            quiz_id=completed_quiz.id,
        )
        assert snapshot["quiz_id"] == completed_quiz.id
        assert snapshot["era_name"] == "Early Church"
        assert snapshot["difficulty"] == "intermediate"
        assert snapshot["score"] == 9
        assert snapshot["total_questions"] == 10
        assert snapshot["percentage_score"] == 90
        assert snapshot["passed"] is True
        assert "completed_at" in snapshot

    def test_build_quiz_snapshot_not_found(self, user):
        """Test 404 when quiz not found."""
        from django.http import Http404

        with pytest.raises(Http404):
            build_content_snapshot(
                user=user,
                share_type="quiz_result",
                quiz_id=9999,
            )

    def test_build_quiz_snapshot_incomplete_quiz(self, user, era):
        """Test 404 when quiz is not completed."""
        from django.http import Http404

        quiz = Quiz.objects.create(
            user=user,
            era=era,
            difficulty=Quiz.Difficulty.BEGINNER,
            score=0,
            total_questions=10,
            completed_at=None,
        )
        with pytest.raises(Http404):
            build_content_snapshot(
                user=user,
                share_type="quiz_result",
                quiz_id=quiz.id,
            )

    def test_build_progress_snapshot(self, user, era):
        """Test building a progress snapshot."""
        # Create some progress data
        UserProgress.objects.create(
            user=user,
            era=era,
            era_visited=True,
            chat_sessions_count=2,
            quizzes_passed=1,
        )
        Quiz.objects.create(
            user=user,
            era=era,
            difficulty=Quiz.Difficulty.BEGINNER,
            score=8,
            total_questions=10,
            completed_at=timezone.now(),
        )

        snapshot = build_content_snapshot(
            user=user,
            share_type="progress",
        )

        assert "completion_percentage" in snapshot
        assert snapshot["eras_visited"] == 1
        assert snapshot["eras_chatted"] == 1
        assert snapshot["eras_quizzed"] == 1
        assert snapshot["total_eras"] >= 1
        assert snapshot["total_quizzes"] == 1
        assert snapshot["quizzes_passed"] == 1
        assert snapshot["average_score"] == 80.0
        assert "current_streak" in snapshot
        assert "total_chat_sessions" in snapshot
        assert "achievements_unlocked" in snapshot
        assert "total_achievements" in snapshot

    def test_build_progress_snapshot_empty(self, user):
        """Test building a progress snapshot with no data."""
        snapshot = build_content_snapshot(
            user=user,
            share_type="progress",
        )
        assert snapshot["completion_percentage"] == 0
        assert snapshot["eras_visited"] == 0
        assert snapshot["total_quizzes"] == 0
        assert snapshot["average_score"] == 0.0

    def test_build_invalid_share_type(self, user):
        """Test ValueError for invalid share type."""
        with pytest.raises(ValueError, match="Unknown share_type"):
            build_content_snapshot(
                user=user,
                share_type="invalid_type",
            )


# ---------------------------------------------------------------------------
# View tests
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestCreateShareLinkView:
    """Tests for CreateShareLinkView."""

    def test_create_achievement_share_link(
        self, api_client, user, achievement, user_achievement
    ):
        """Test creating a share link for an achievement."""
        api_client.force_authenticate(user=user)
        response = api_client.post(
            "/api/sharing/links/",
            {
                "share_type": "achievement",
                "achievement_id": achievement.id,
            },
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert "token" in response.data
        assert response.data["share_type"] == "achievement"
        assert "share_url" in response.data
        assert "content_snapshot" in response.data
        assert response.data["content_snapshot"]["achievement_name"] == "Perfect Scholar"

    def test_create_quiz_share_link(self, api_client, user, completed_quiz):
        """Test creating a share link for a quiz result."""
        api_client.force_authenticate(user=user)
        response = api_client.post(
            "/api/sharing/links/",
            {
                "share_type": "quiz_result",
                "quiz_id": completed_quiz.id,
            },
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["share_type"] == "quiz_result"
        assert response.data["content_snapshot"]["percentage_score"] == 90

    def test_create_progress_share_link(self, api_client, user):
        """Test creating a share link for progress."""
        api_client.force_authenticate(user=user)
        response = api_client.post(
            "/api/sharing/links/",
            {"share_type": "progress"},
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["share_type"] == "progress"
        assert "completion_percentage" in response.data["content_snapshot"]

    def test_create_share_link_uses_display_name(
        self, api_client, user, achievement, user_achievement
    ):
        """Test that share link uses user's display name."""
        api_client.force_authenticate(user=user)
        response = api_client.post(
            "/api/sharing/links/",
            {
                "share_type": "achievement",
                "achievement_id": achievement.id,
            },
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["sharer_display_name"] == "Test Sharer"

    def test_create_share_link_missing_achievement_id(self, api_client, user):
        """Test validation error when achievement_id missing."""
        api_client.force_authenticate(user=user)
        response = api_client.post(
            "/api/sharing/links/",
            {"share_type": "achievement"},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_share_link_missing_quiz_id(self, api_client, user):
        """Test validation error when quiz_id missing."""
        api_client.force_authenticate(user=user)
        response = api_client.post(
            "/api/sharing/links/",
            {"share_type": "quiz_result"},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_share_link_invalid_share_type(self, api_client, user):
        """Test validation error for invalid share type."""
        api_client.force_authenticate(user=user)
        response = api_client.post(
            "/api/sharing/links/",
            {"share_type": "invalid"},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_share_link_unauthenticated(self, api_client):
        """Test that unauthenticated requests are rejected."""
        response = api_client.post(
            "/api/sharing/links/",
            {"share_type": "progress"},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_share_link_achievement_not_found(self, api_client, user):
        """Test 404 when achievement does not exist."""
        api_client.force_authenticate(user=user)
        response = api_client.post(
            "/api/sharing/links/",
            {
                "share_type": "achievement",
                "achievement_id": 9999,
            },
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_create_share_link_quiz_not_found(self, api_client, user):
        """Test 404 when quiz does not exist."""
        api_client.force_authenticate(user=user)
        response = api_client.post(
            "/api/sharing/links/",
            {
                "share_type": "quiz_result",
                "quiz_id": 9999,
            },
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestListShareLinksView:
    """Tests for ListShareLinksView."""

    def test_list_share_links(self, api_client, user, share_link):
        """Test listing user's share links."""
        api_client.force_authenticate(user=user)
        response = api_client.get("/api/sharing/links/list/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["token"] == share_link.token

    def test_list_share_links_empty(self, api_client, user):
        """Test listing when user has no share links."""
        api_client.force_authenticate(user=user)
        response = api_client.get("/api/sharing/links/list/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 0
        assert response.data["results"] == []

    def test_list_share_links_excludes_inactive(self, api_client, user, share_link):
        """Test that deactivated links are excluded."""
        share_link.is_active = False
        share_link.save()

        api_client.force_authenticate(user=user)
        response = api_client.get("/api/sharing/links/list/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 0

    def test_list_share_links_only_own(self, api_client, user, other_user, share_link):
        """Test that users only see their own share links."""
        api_client.force_authenticate(user=other_user)
        response = api_client.get("/api/sharing/links/list/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 0

    def test_list_share_links_unauthenticated(self, api_client):
        """Test that unauthenticated requests are rejected."""
        response = api_client.get("/api/sharing/links/list/")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestDeleteShareLinkView:
    """Tests for DeleteShareLinkView."""

    def test_delete_share_link(self, api_client, user, share_link):
        """Test soft-deleting a share link."""
        api_client.force_authenticate(user=user)
        response = api_client.delete(
            f"/api/sharing/links/{share_link.token}/"
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

        share_link.refresh_from_db()
        assert share_link.is_active is False

    def test_delete_share_link_not_found(self, api_client, user):
        """Test 404 when token does not exist."""
        api_client.force_authenticate(user=user)
        response = api_client.delete("/api/sharing/links/nonexistent/")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_share_link_other_user(self, api_client, other_user, share_link):
        """Test that users cannot delete other users' share links."""
        api_client.force_authenticate(user=other_user)
        response = api_client.delete(
            f"/api/sharing/links/{share_link.token}/"
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

        share_link.refresh_from_db()
        assert share_link.is_active is True

    def test_delete_share_link_already_inactive(self, api_client, user, share_link):
        """Test 404 when trying to delete already deactivated link."""
        share_link.is_active = False
        share_link.save()

        api_client.force_authenticate(user=user)
        response = api_client.delete(
            f"/api/sharing/links/{share_link.token}/"
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_share_link_unauthenticated(self, api_client, share_link):
        """Test that unauthenticated requests are rejected."""
        response = api_client.delete(
            f"/api/sharing/links/{share_link.token}/"
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestPublicSharePage:
    """Tests for public_share_page view."""

    def test_public_share_page_achievement(self, client, share_link):
        """Test rendering an achievement share page."""
        response = client.get(f"/share/{share_link.token}/")

        assert response.status_code == 200
        content = response.content.decode()
        assert "Perfect Scholar" in content
        assert "og:title" in content
        assert "Toledot" in content
        assert "Achievement Unlocked" in content

    def test_public_share_page_quiz_result(self, client, user):
        """Test rendering a quiz result share page."""
        link = ShareLink.objects.create(
            user=user,
            share_type=ShareLink.ShareType.QUIZ_RESULT,
            content_snapshot={
                "quiz_id": 1,
                "era_name": "Early Church",
                "difficulty": "intermediate",
                "score": 9,
                "total_questions": 10,
                "percentage_score": 90,
                "passed": True,
                "completed_at": "2026-02-17T10:45:00+00:00",
            },
            sharer_display_name="Test Sharer",
        )

        response = client.get(f"/share/{link.token}/")

        assert response.status_code == 200
        content = response.content.decode()
        assert "Quiz Result" in content
        assert "Early Church" in content
        assert "90%" in content
        assert "Passed" in content

    def test_public_share_page_progress(self, client, user):
        """Test rendering a progress share page."""
        link = ShareLink.objects.create(
            user=user,
            share_type=ShareLink.ShareType.PROGRESS,
            content_snapshot={
                "completion_percentage": 67,
                "eras_visited": 5,
                "eras_chatted": 4,
                "eras_quizzed": 3,
                "total_eras": 6,
                "total_quizzes": 15,
                "quizzes_passed": 12,
                "average_score": 82.5,
                "current_streak": 5,
                "total_chat_sessions": 20,
                "achievements_unlocked": 8,
                "total_achievements": 13,
            },
            sharer_display_name="Test Sharer",
        )

        response = client.get(f"/share/{link.token}/")

        assert response.status_code == 200
        content = response.content.decode()
        assert "Learning Journey" in content
        assert "67%" in content
        assert "5/6" in content
        assert "5-day streak" in content

    def test_public_share_page_increments_view_count(self, client, share_link):
        """Test that viewing the page increments view_count."""
        assert share_link.view_count == 0

        client.get(f"/share/{share_link.token}/")
        share_link.refresh_from_db()
        assert share_link.view_count == 1

        client.get(f"/share/{share_link.token}/")
        share_link.refresh_from_db()
        assert share_link.view_count == 2

    def test_public_share_page_not_found(self, client):
        """Test 404 for nonexistent token."""
        response = client.get("/share/nonexistent/")

        assert response.status_code == 404

    def test_public_share_page_inactive_link(self, client, share_link):
        """Test 404 for deactivated share link."""
        share_link.is_active = False
        share_link.save()

        response = client.get(f"/share/{share_link.token}/")

        assert response.status_code == 404

    def test_public_share_page_og_tags(self, client, share_link):
        """Test that OG meta tags are present."""
        response = client.get(f"/share/{share_link.token}/")

        content = response.content.decode()
        assert 'property="og:title"' in content
        assert 'property="og:description"' in content
        assert 'property="og:type"' in content
        assert 'property="og:url"' in content
        assert 'property="og:site_name"' in content

    def test_public_share_page_twitter_tags(self, client, share_link):
        """Test that Twitter Card meta tags are present."""
        response = client.get(f"/share/{share_link.token}/")

        content = response.content.decode()
        assert 'name="twitter:card"' in content
        assert 'name="twitter:title"' in content
        assert 'name="twitter:description"' in content

    def test_public_share_page_cta_button(self, client, share_link):
        """Test that the CTA button is present."""
        response = client.get(f"/share/{share_link.token}/")

        content = response.content.decode()
        assert "Start Your Own Journey" in content

    def test_public_share_page_no_auth_required(self, client, share_link):
        """Test that the page is accessible without authentication."""
        # client is the default Django test client (no auth)
        response = client.get(f"/share/{share_link.token}/")

        assert response.status_code == 200
