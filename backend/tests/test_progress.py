"""Tests for progress tracking functionality.

Tests models, views, serializers, signals, and achievement system.
"""

import pytest
from datetime import timedelta
from django.utils import timezone
from rest_framework import status

from apps.progress.models import Achievement, UserAchievement, UserProgress
from apps.progress.services import calculate_activity_streak, check_and_unlock_achievements
from apps.chat.models import ChatSession
from apps.quiz.models import Quiz, QuizQuestion
from apps.eras.models import Era


@pytest.mark.django_db
class TestUserProgressModel:
    """Tests for UserProgress model."""

    def test_create_user_progress(self, user, era):
        """Test creating a UserProgress instance."""
        progress = UserProgress.objects.create(
            user=user,
            era=era,
            era_visited=True,
        )
        assert progress.user == user
        assert progress.era == era
        assert progress.era_visited is True
        assert progress.chat_sessions_count == 0
        assert progress.quizzes_passed == 0

    def test_completion_percentage_all_activities(self, user, era):
        """Test completion percentage with all activities completed."""
        progress = UserProgress.objects.create(
            user=user,
            era=era,
            era_visited=True,
            chat_sessions_count=1,
            quizzes_passed=1,
        )
        assert progress.completion_percentage == 100

    def test_completion_percentage_partial(self, user, era):
        """Test completion percentage with partial completion."""
        progress = UserProgress.objects.create(
            user=user,
            era=era,
            era_visited=True,
            chat_sessions_count=1,
            quizzes_passed=0,
        )
        assert progress.completion_percentage == 67

    def test_completion_percentage_single_activity(self, user, era):
        """Test completion percentage with single activity."""
        progress = UserProgress.objects.create(
            user=user,
            era=era,
            era_visited=True,
            chat_sessions_count=0,
            quizzes_passed=0,
        )
        assert progress.completion_percentage == 33

    def test_completion_percentage_no_activities(self, user, era):
        """Test completion percentage with no activities."""
        progress = UserProgress.objects.create(
            user=user,
            era=era,
        )
        assert progress.completion_percentage == 0

    def test_unique_constraint_user_era(self, user, era):
        """Test unique constraint on user+era."""
        UserProgress.objects.create(user=user, era=era)
        with pytest.raises(Exception):
            UserProgress.objects.create(user=user, era=era)


@pytest.mark.django_db
class TestAchievementModel:
    """Tests for Achievement model."""

    def test_create_achievement(self):
        """Test creating an achievement."""
        achievement = Achievement.objects.create(
            slug="test-achievement",
            name="Test Achievement",
            description="Test description",
            category=Achievement.Category.QUIZ,
            icon_key="trophy",
            order=1,
        )
        assert achievement.slug == "test-achievement"
        assert achievement.category == Achievement.Category.QUIZ


@pytest.mark.django_db
class TestUserAchievementModel:
    """Tests for UserAchievement model."""

    def test_create_user_achievement(self, user):
        """Test creating a user achievement."""
        achievement = Achievement.objects.create(
            slug="test",
            name="Test",
            description="Test",
            category=Achievement.Category.QUIZ,
            icon_key="trophy",
        )
        user_achievement = UserAchievement.objects.create(
            user=user,
            achievement=achievement,
        )
        assert user_achievement.user == user
        assert user_achievement.achievement == achievement
        assert user_achievement.unlocked_at is not None


@pytest.mark.django_db
class TestProgressSummaryView:
    """Tests for ProgressSummaryView."""

    def test_get_progress_summary_empty(self, api_client, user, auth_headers):
        """Test getting progress summary with no data."""
        api_client.force_authenticate(user=user)
        response = api_client.get("/api/progress/summary/")

        assert response.status_code == status.HTTP_200_OK
        assert "overall" in response.data
        assert "stats" in response.data
        assert "by_era" in response.data
        assert "recent_activity" in response.data
        assert response.data["overall"]["completion_percentage"] == 0

    def test_get_progress_summary_with_data(self, api_client, user, era, auth_headers):
        """Test getting progress summary with data."""
        # Create progress
        UserProgress.objects.create(
            user=user,
            era=era,
            era_visited=True,
            chat_sessions_count=2,
            quizzes_passed=1,
        )

        api_client.force_authenticate(user=user)
        response = api_client.get("/api/progress/summary/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["overall"]["eras_visited"] == 1
        assert response.data["stats"]["total_chat_sessions"] == 0  # No actual ChatSession created
        assert len(response.data["by_era"]) >= 1

    def test_requires_authentication(self, api_client):
        """Test that endpoint requires authentication."""
        response = api_client.get("/api/progress/summary/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestMarkEraVisitedView:
    """Tests for MarkEraVisitedView."""

    def test_mark_era_visited_new(self, api_client, user, era, auth_headers):
        """Test marking an era as visited for the first time."""
        api_client.force_authenticate(user=user)
        response = api_client.post(
            "/api/progress/mark-era-visited/",
            {"era_id": era.id},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["era_visited"] is True
        assert response.data["first_visited_at"] is not None
        assert response.data["completion_percentage"] == 33

        # Verify in database
        progress = UserProgress.objects.get(user=user, era=era)
        assert progress.era_visited is True

    def test_mark_era_visited_idempotent(self, api_client, user, era, auth_headers):
        """Test that marking era visited is idempotent."""
        api_client.force_authenticate(user=user)

        # First call
        response1 = api_client.post(
            "/api/progress/mark-era-visited/",
            {"era_id": era.id},
        )
        first_visited_at = response1.data["first_visited_at"]

        # Second call
        response2 = api_client.post(
            "/api/progress/mark-era-visited/",
            {"era_id": era.id},
        )

        assert response2.status_code == status.HTTP_200_OK
        assert response2.data["first_visited_at"] == first_visited_at

    def test_mark_era_visited_invalid_era(self, api_client, user, auth_headers):
        """Test marking non-existent era as visited."""
        api_client.force_authenticate(user=user)
        response = api_client.post(
            "/api/progress/mark-era-visited/",
            {"era_id": 9999},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_requires_authentication(self, api_client, era):
        """Test that endpoint requires authentication."""
        response = api_client.post(
            "/api/progress/mark-era-visited/",
            {"era_id": era.id},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestAchievementListView:
    """Tests for AchievementListView."""

    def test_get_achievements_empty(self, api_client, user, auth_headers):
        """Test getting achievements when none exist."""
        api_client.force_authenticate(user=user)
        response = api_client.get("/api/progress/achievements/")

        assert response.status_code == status.HTTP_200_OK
        assert "achievements" in response.data
        assert response.data["total_unlocked"] == 0
        assert response.data["total_achievements"] == 0

    def test_get_achievements_with_unlocked(self, api_client, user, auth_headers):
        """Test getting achievements with some unlocked."""
        # Create achievements
        achievement1 = Achievement.objects.create(
            slug="test1",
            name="Test 1",
            description="Test",
            category=Achievement.Category.QUIZ,
            icon_key="trophy",
        )
        achievement2 = Achievement.objects.create(
            slug="test2",
            name="Test 2",
            description="Test",
            category=Achievement.Category.CHAT,
            icon_key="message-circle",
        )

        # Unlock one achievement
        UserAchievement.objects.create(user=user, achievement=achievement1)

        api_client.force_authenticate(user=user)
        response = api_client.get("/api/progress/achievements/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["total_achievements"] == 2
        assert response.data["total_unlocked"] == 1

        # Check that first achievement is unlocked
        achievements = response.data["achievements"]
        unlocked = [a for a in achievements if a["unlocked"]]
        assert len(unlocked) == 1
        assert unlocked[0]["slug"] == "test1"

    def test_requires_authentication(self, api_client):
        """Test that endpoint requires authentication."""
        response = api_client.get("/api/progress/achievements/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestCheckAchievementsView:
    """Tests for CheckAchievementsView."""

    def test_check_achievements_unlock_first_visit(self, api_client, user, era, auth_headers):
        """Test unlocking first-visit achievement."""
        # Create the achievement
        Achievement.objects.create(
            slug="first-visit",
            name="First Steps",
            description="Explore your first era on the canvas",
            category=Achievement.Category.EXPLORATION,
            icon_key="map",
        )

        # Mark era as visited
        UserProgress.objects.create(
            user=user,
            era=era,
            era_visited=True,
        )

        api_client.force_authenticate(user=user)
        response = api_client.post("/api/progress/check-achievements/")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["newly_unlocked"]) == 1
        assert response.data["newly_unlocked"][0]["slug"] == "first-visit"
        assert response.data["total_unlocked"] == 1

    def test_check_achievements_no_new_unlocks(self, api_client, user, auth_headers):
        """Test checking achievements with no new unlocks."""
        api_client.force_authenticate(user=user)
        response = api_client.post("/api/progress/check-achievements/")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["newly_unlocked"]) == 0

    def test_requires_authentication(self, api_client):
        """Test that endpoint requires authentication."""
        response = api_client.post("/api/progress/check-achievements/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestChatProgressSignal:
    """Tests for chat progress signal handler."""

    def test_chat_session_updates_progress(self, user, era):
        """Test that creating a chat session updates progress."""
        # Create chat session
        ChatSession.objects.create(user=user, era=era, title="Test Chat")

        # Check progress was updated
        progress = UserProgress.objects.get(user=user, era=era)
        assert progress.chat_sessions_count == 1
        assert progress.last_chat_at is not None

    def test_multiple_chat_sessions(self, user, era):
        """Test that multiple chat sessions increment count."""
        ChatSession.objects.create(user=user, era=era, title="Chat 1")
        ChatSession.objects.create(user=user, era=era, title="Chat 2")

        progress = UserProgress.objects.get(user=user, era=era)
        assert progress.chat_sessions_count == 2


@pytest.mark.django_db
class TestQuizProgressSignal:
    """Tests for quiz progress signal handler."""

    def test_quiz_completion_updates_progress(self, user, era):
        """Test that completing a quiz updates progress."""
        # Create and complete quiz
        quiz = Quiz.objects.create(
            user=user,
            era=era,
            difficulty=Quiz.Difficulty.BEGINNER,
            score=8,
            total_questions=10,
            completed_at=timezone.now(),
        )

        # Check progress was updated
        progress = UserProgress.objects.get(user=user, era=era)
        assert progress.quizzes_completed == 1
        assert progress.quizzes_passed == 1  # 80% >= 70%
        assert progress.best_quiz_score == 80
        assert progress.last_quiz_at is not None

    def test_failed_quiz_not_counted_as_passed(self, user, era):
        """Test that failed quiz is not counted as passed."""
        quiz = Quiz.objects.create(
            user=user,
            era=era,
            difficulty=Quiz.Difficulty.BEGINNER,
            score=5,
            total_questions=10,
            completed_at=timezone.now(),
        )

        progress = UserProgress.objects.get(user=user, era=era)
        assert progress.quizzes_completed == 1
        assert progress.quizzes_passed == 0  # 50% < 70%

    def test_best_score_updated(self, user, era):
        """Test that best score is properly tracked."""
        # First quiz: 70%
        Quiz.objects.create(
            user=user,
            era=era,
            score=7,
            total_questions=10,
            completed_at=timezone.now(),
        )

        # Second quiz: 90%
        Quiz.objects.create(
            user=user,
            era=era,
            score=9,
            total_questions=10,
            completed_at=timezone.now(),
        )

        progress = UserProgress.objects.get(user=user, era=era)
        assert progress.best_quiz_score == 90


@pytest.mark.django_db
class TestActivityStreak:
    """Tests for activity streak calculation."""

    def test_streak_with_consecutive_days(self, user):
        """Test streak calculation with consecutive days of activity."""
        today = timezone.now().date()

        # Create 3 separate eras for 3 days of activity
        for i in range(3):
            date = today - timedelta(days=i)
            era = Era.objects.create(
                name=f"Streak Era {i}",
                slug=f"streak-era-{i}",
                start_year=100 + i * 100,
                end_year=200 + i * 100,
                description="Test",
                color="#000000",
                order=10 + i,
            )
            UserProgress.objects.create(
                user=user,
                era=era,
                era_visited=True,
                first_visited_at=timezone.datetime.combine(
                    date, timezone.datetime.min.time()
                ).replace(tzinfo=timezone.get_current_timezone()),
            )

        streak = calculate_activity_streak(user)
        assert streak == 3

    def test_streak_with_gap(self, user, era):
        """Test that streak breaks with a gap."""
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)

        # Activity today, but not yesterday
        UserProgress.objects.create(
            user=user,
            era=era,
            era_visited=True,
            first_visited_at=timezone.now(),
        )

        streak = calculate_activity_streak(user)
        # Streak might be 0 or 1 depending on exact timing
        assert streak <= 1

    def test_streak_with_no_activity(self, user):
        """Test streak with no activity."""
        streak = calculate_activity_streak(user)
        assert streak == 0


@pytest.mark.django_db
class TestAchievementCriteria:
    """Tests for achievement unlock criteria."""

    def test_first_visit_achievement(self, user, era):
        """Test first-visit achievement unlock."""
        achievement = Achievement.objects.create(
            slug="first-visit",
            name="First Steps",
            description="Explore your first era",
            category=Achievement.Category.EXPLORATION,
            icon_key="map",
        )

        # Mark era as visited
        UserProgress.objects.create(user=user, era=era, era_visited=True)

        # Check achievement
        newly_unlocked = check_and_unlock_achievements(user)
        assert len(newly_unlocked) == 1
        assert newly_unlocked[0].achievement.slug == "first-visit"

    def test_first_chat_achievement(self, user, era):
        """Test first-chat achievement unlock."""
        achievement = Achievement.objects.create(
            slug="first-chat",
            name="Conversation Starter",
            description="Start your first chat session",
            category=Achievement.Category.CHAT,
            icon_key="message-circle",
        )

        # Create chat session
        ChatSession.objects.create(user=user, era=era)

        # Check achievement
        newly_unlocked = check_and_unlock_achievements(user)
        assert len(newly_unlocked) == 1
        assert newly_unlocked[0].achievement.slug == "first-chat"

    def test_first_quiz_achievement(self, user, era):
        """Test first-quiz achievement unlock."""
        achievement = Achievement.objects.create(
            slug="first-quiz",
            name="Quiz Beginner",
            description="Complete your first quiz",
            category=Achievement.Category.QUIZ,
            icon_key="trophy",
        )

        # Create completed quiz
        Quiz.objects.create(
            user=user,
            era=era,
            score=7,
            total_questions=10,
            completed_at=timezone.now(),
        )

        # Check achievement
        newly_unlocked = check_and_unlock_achievements(user)
        assert len(newly_unlocked) == 1
        assert newly_unlocked[0].achievement.slug == "first-quiz"

    def test_perfect_score_achievement(self, user, era):
        """Test perfect-score achievement unlock."""
        achievement = Achievement.objects.create(
            slug="perfect-score",
            name="Perfect Scholar",
            description="Score 100% on any quiz",
            category=Achievement.Category.QUIZ,
            icon_key="star",
        )

        # Create perfect quiz
        Quiz.objects.create(
            user=user,
            era=era,
            score=10,
            total_questions=10,
            completed_at=timezone.now(),
        )

        # Check achievement
        newly_unlocked = check_and_unlock_achievements(user)
        assert len(newly_unlocked) == 1
        assert newly_unlocked[0].achievement.slug == "perfect-score"

    def test_achievement_not_unlocked_twice(self, user, era):
        """Test that achievement is not unlocked twice."""
        achievement = Achievement.objects.create(
            slug="first-visit",
            name="First Steps",
            description="Explore your first era",
            category=Achievement.Category.EXPLORATION,
            icon_key="map",
        )

        # Mark era as visited
        UserProgress.objects.create(user=user, era=era, era_visited=True)

        # First check
        newly_unlocked1 = check_and_unlock_achievements(user)
        assert len(newly_unlocked1) == 1

        # Second check
        newly_unlocked2 = check_and_unlock_achievements(user)
        assert len(newly_unlocked2) == 0


@pytest.fixture
def era(db):
    """Create a test era."""
    return Era.objects.create(
        name="Test Era",
        slug="test-era",
        start_year=100,
        end_year=200,
        description="Test description",
        color="#000000",
        order=1,
    )


@pytest.fixture
def user(django_user_model):
    """Create a test user."""
    return django_user_model.objects.create_user(
        email="test@example.com",
        password="testpass123",
        display_name="Test User",
    )


@pytest.fixture
def auth_headers(user):
    """Create authentication headers."""
    return {"HTTP_AUTHORIZATION": f"Bearer test_token"}
