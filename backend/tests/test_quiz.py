"""Comprehensive tests for P6 Fun Tests & Quizzes.

Tests cover models, serializers, API endpoints, and service functions
for the quiz app's AI-powered quiz generation and grading.
"""

from unittest.mock import MagicMock, patch

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.eras.models import Era, KeyEvent, KeyFigure
from apps.quiz.models import Quiz, QuizQuestion
from apps.quiz.serializers import (
    QuizAnswerSerializer,
    QuizCreateSerializer,
    QuizListSerializer,
    QuizQuestionDetailSerializer,
    QuizQuestionSerializer,
    QuizSerializer,
)


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def user(create_user):
    """Create a test user."""
    return create_user(
        email="quizuser@example.com",
        username="quizuser",
        password="testpass123",
    )


@pytest.fixture
def other_user(create_user):
    """Create a second test user for permission tests."""
    return create_user(
        email="other@example.com",
        username="otheruser",
        password="testpass123",
    )


@pytest.fixture
def authenticated_client(user):
    """Create an authenticated API client for the test user."""
    client = APIClient()
    refresh = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return client


@pytest.fixture
def other_authenticated_client(other_user):
    """Create an authenticated API client for the other user."""
    client = APIClient()
    refresh = RefreshToken.for_user(other_user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return client


@pytest.fixture
def sample_era(db):
    """Create a sample era with key events and figures."""
    era = Era.objects.create(
        name="Early Church",
        slug="early-church",
        start_year=33,
        end_year=325,
        description="The period of the early Christian church.",
        summary="The apostolic age and early church fathers.",
        color="#3B82F6",
        order=1,
    )

    # Add key events
    KeyEvent.objects.create(
        era=era,
        year=325,
        title="Council of Nicaea",
        description="First ecumenical council, produced the Nicene Creed.",
    )

    # Add key figures
    KeyFigure.objects.create(
        era=era,
        name="Augustine of Hippo",
        birth_year=354,
        death_year=430,
        title="Bishop of Hippo",
        description="Influential theologian and philosopher.",
    )

    return era


@pytest.fixture
def quiz(db, user, sample_era):
    """Create a test quiz."""
    return Quiz.objects.create(
        user=user,
        era=sample_era,
        difficulty=Quiz.Difficulty.BEGINNER,
        total_questions=5,
    )


@pytest.fixture
def completed_quiz(db, user, sample_era):
    """Create a completed test quiz with questions."""
    from django.utils import timezone

    quiz = Quiz.objects.create(
        user=user,
        era=sample_era,
        difficulty=Quiz.Difficulty.INTERMEDIATE,
        score=4,
        total_questions=5,
        completed_at=timezone.now(),
    )

    # Add questions
    QuizQuestion.objects.create(
        quiz=quiz,
        question_text="What year was the Council of Nicaea?",
        question_type=QuizQuestion.QuestionType.MULTIPLE_CHOICE,
        options=["313", "325", "381", "451"],
        correct_answer="1",
        user_answer="1",
        is_correct=True,
        explanation="The Council of Nicaea was held in 325 AD.",
        order=1,
    )

    QuizQuestion.objects.create(
        quiz=quiz,
        question_text="Augustine was the Bishop of Hippo.",
        question_type=QuizQuestion.QuestionType.TRUE_FALSE,
        options=["True", "False"],
        correct_answer="0",
        user_answer="0",
        is_correct=True,
        explanation="Augustine served as Bishop of Hippo from 395-430 AD.",
        order=2,
    )

    return quiz


@pytest.fixture
def quiz_question(db, quiz):
    """Create a test quiz question."""
    return QuizQuestion.objects.create(
        quiz=quiz,
        question_text="What year was the Council of Nicaea?",
        question_type=QuizQuestion.QuestionType.MULTIPLE_CHOICE,
        options=["313", "325", "381", "451"],
        correct_answer="1",
        explanation="The Council of Nicaea was held in 325 AD.",
        order=1,
    )


# =============================================================================
# Model Tests
# =============================================================================


@pytest.mark.django_db
class TestQuizModel:
    """Test Quiz model."""

    def test_quiz_creation(self, user, sample_era):
        """Test creating a quiz."""
        quiz = Quiz.objects.create(
            user=user,
            era=sample_era,
            difficulty=Quiz.Difficulty.BEGINNER,
            total_questions=10,
        )

        assert quiz.user == user
        assert quiz.era == sample_era
        assert quiz.difficulty == Quiz.Difficulty.BEGINNER
        assert quiz.total_questions == 10
        assert quiz.score == 0
        assert quiz.completed_at is None

    def test_quiz_is_completed_property(self, quiz):
        """Test is_completed property."""
        assert not quiz.is_completed

        from django.utils import timezone

        quiz.completed_at = timezone.now()
        quiz.save()

        assert quiz.is_completed

    def test_quiz_percentage_score_property(self, quiz):
        """Test percentage_score property."""
        quiz.score = 8
        quiz.total_questions = 10
        quiz.save()

        assert quiz.percentage_score == 80

    def test_quiz_percentage_score_zero_questions(self, quiz):
        """Test percentage_score with zero questions."""
        quiz.total_questions = 0
        quiz.save()

        assert quiz.percentage_score == 0

    def test_quiz_passed_property(self, quiz):
        """Test passed property."""
        quiz.score = 7
        quiz.total_questions = 10
        quiz.save()

        assert quiz.passed

        quiz.score = 6
        quiz.save()

        assert not quiz.passed

    def test_quiz_str_method(self, quiz):
        """Test __str__ method."""
        assert "quizuser@example.com" in str(quiz)
        assert "Early Church" in str(quiz)
        assert "beginner" in str(quiz)


@pytest.mark.django_db
class TestQuizQuestionModel:
    """Test QuizQuestion model."""

    def test_question_creation(self, quiz):
        """Test creating a quiz question."""
        question = QuizQuestion.objects.create(
            quiz=quiz,
            question_text="What is the significance of Nicaea?",
            question_type=QuizQuestion.QuestionType.SHORT_ANSWER,
            correct_answer="It established the Nicene Creed.",
            explanation="The Council of Nicaea produced the Nicene Creed.",
            order=1,
        )

        assert question.quiz == quiz
        assert question.question_type == QuizQuestion.QuestionType.SHORT_ANSWER
        assert question.is_correct is None
        assert question.user_answer == ""

    def test_question_ordering(self, quiz):
        """Test question ordering."""
        q1 = QuizQuestion.objects.create(
            quiz=quiz,
            question_text="Question 1",
            question_type=QuizQuestion.QuestionType.MULTIPLE_CHOICE,
            options=["A", "B", "C", "D"],
            correct_answer="0",
            explanation="Explanation 1",
            order=2,
        )
        q2 = QuizQuestion.objects.create(
            quiz=quiz,
            question_text="Question 2",
            question_type=QuizQuestion.QuestionType.MULTIPLE_CHOICE,
            options=["A", "B", "C", "D"],
            correct_answer="0",
            explanation="Explanation 2",
            order=1,
        )

        questions = list(quiz.questions.all())
        assert questions[0] == q2
        assert questions[1] == q1


# =============================================================================
# Serializer Tests
# =============================================================================


@pytest.mark.django_db
class TestQuizSerializers:
    """Test quiz serializers."""

    def test_quiz_question_serializer(self, quiz_question):
        """Test QuizQuestionSerializer (hides correct answer)."""
        serializer = QuizQuestionSerializer(quiz_question)
        data = serializer.data

        assert data["id"] == quiz_question.id
        assert data["question_text"] == quiz_question.question_text
        assert "correct_answer" not in data
        assert "explanation" not in data

    def test_quiz_question_detail_serializer(self, quiz_question):
        """Test QuizQuestionDetailSerializer (shows all fields)."""
        serializer = QuizQuestionDetailSerializer(quiz_question)
        data = serializer.data

        assert data["id"] == quiz_question.id
        assert data["question_text"] == quiz_question.question_text
        assert data["correct_answer"] == quiz_question.correct_answer
        assert data["explanation"] == quiz_question.explanation

    def test_quiz_list_serializer(self, completed_quiz):
        """Test QuizListSerializer."""
        serializer = QuizListSerializer(completed_quiz)
        data = serializer.data

        assert data["id"] == completed_quiz.id
        assert data["era_name"] == "Early Church"
        assert data["percentage_score"] == 80
        assert data["passed"] is True
        assert "questions" not in data

    def test_quiz_serializer_in_progress(self, quiz, quiz_question):
        """Test QuizSerializer for in-progress quiz (hides answers)."""
        serializer = QuizSerializer(quiz)
        data = serializer.data

        assert data["id"] == quiz.id
        assert len(data["questions"]) == 1
        assert "correct_answer" not in data["questions"][0]

    def test_quiz_serializer_completed(self, completed_quiz):
        """Test QuizSerializer for completed quiz (shows answers)."""
        serializer = QuizSerializer(completed_quiz)
        data = serializer.data

        assert data["id"] == completed_quiz.id
        assert len(data["questions"]) == 2
        assert "correct_answer" in data["questions"][0]
        assert "explanation" in data["questions"][0]

    def test_quiz_create_serializer_validation(self):
        """Test QuizCreateSerializer validation."""
        serializer = QuizCreateSerializer(
            data={
                "difficulty": "beginner",
                "question_count": 10,
            }
        )
        assert serializer.is_valid()

        # Test invalid question count
        serializer = QuizCreateSerializer(
            data={
                "difficulty": "beginner",
                "question_count": 15,
            }
        )
        assert not serializer.is_valid()

    def test_quiz_answer_serializer(self):
        """Test QuizAnswerSerializer."""
        serializer = QuizAnswerSerializer(
            data={
                "question_id": 1,
                "answer": "1",
            }
        )
        assert serializer.is_valid()


# =============================================================================
# API Endpoint Tests
# =============================================================================


@pytest.mark.django_db
class TestQuizAPI:
    """Test Quiz API endpoints."""

    def test_list_quizzes(self, authenticated_client, completed_quiz):
        """Test listing user's quizzes."""
        url = reverse("quiz:quiz-list")
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["id"] == completed_quiz.id

    def test_list_quizzes_unauthenticated(self):
        """Test listing quizzes without authentication."""
        client = APIClient()
        url = reverse("quiz:quiz-list")
        response = client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_quizzes_filter_by_era(self, authenticated_client, completed_quiz):
        """Test filtering quizzes by era."""
        url = reverse("quiz:quiz-list")
        response = authenticated_client.get(url, {"era": completed_quiz.era.id})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1

    def test_list_quizzes_filter_by_completion(
        self, authenticated_client, quiz, completed_quiz
    ):
        """Test filtering quizzes by completion status."""
        url = reverse("quiz:quiz-list")

        # Filter for completed quizzes
        response = authenticated_client.get(url, {"completed": "true"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["id"] == completed_quiz.id

        # Filter for in-progress quizzes
        response = authenticated_client.get(url, {"completed": "false"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["id"] == quiz.id

    def test_retrieve_quiz(self, authenticated_client, completed_quiz):
        """Test retrieving a specific quiz."""
        url = reverse("quiz:quiz-detail", kwargs={"pk": completed_quiz.id})
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == completed_quiz.id
        assert len(response.data["questions"]) == 2

    def test_retrieve_quiz_permission(
        self, authenticated_client, other_authenticated_client, completed_quiz
    ):
        """Test that users can only retrieve their own quizzes."""
        url = reverse("quiz:quiz-detail", kwargs={"pk": completed_quiz.id})
        response = other_authenticated_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @patch("apps.quiz.views.generate_quiz_questions")
    def test_create_quiz(
        self, mock_generate, authenticated_client, sample_era, user
    ):
        """Test creating a new quiz."""
        url = reverse("quiz:quiz-list")
        data = {
            "era_id": sample_era.id,
            "difficulty": "beginner",
            "question_count": 5,
        }

        response = authenticated_client.post(url, data)

        assert response.status_code == status.HTTP_201_CREATED
        assert mock_generate.called

        # Verify quiz was created
        quiz = Quiz.objects.get(id=response.data["id"])
        assert quiz.user == user
        assert quiz.era == sample_era
        assert quiz.total_questions == 5

    @patch("apps.quiz.views.generate_quiz_questions")
    def test_create_quiz_all_eras(self, mock_generate, authenticated_client, user):
        """Test creating an 'All Eras' quiz."""
        url = reverse("quiz:quiz-list")
        data = {
            "difficulty": "intermediate",
            "question_count": 10,
        }

        response = authenticated_client.post(url, data)

        assert response.status_code == status.HTTP_201_CREATED

        # Verify quiz was created with null era
        quiz = Quiz.objects.get(id=response.data["id"])
        assert quiz.era is None
        assert quiz.total_questions == 10

    def test_submit_answer_multiple_choice(
        self, authenticated_client, quiz, quiz_question
    ):
        """Test submitting a multiple choice answer."""
        url = reverse("quiz:quiz-submit-answer", kwargs={"pk": quiz.id})
        data = {
            "question_id": quiz_question.id,
            "answer": "1",
        }

        response = authenticated_client.post(url, data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["is_correct"] is True
        assert response.data["explanation"] == quiz_question.explanation

        # Verify question was updated
        quiz_question.refresh_from_db()
        assert quiz_question.user_answer == "1"
        assert quiz_question.is_correct is True

    def test_submit_answer_incorrect(self, authenticated_client, quiz, quiz_question):
        """Test submitting an incorrect answer."""
        url = reverse("quiz:quiz-submit-answer", kwargs={"pk": quiz.id})
        data = {
            "question_id": quiz_question.id,
            "answer": "2",
        }

        response = authenticated_client.post(url, data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["is_correct"] is False

        quiz_question.refresh_from_db()
        assert quiz_question.is_correct is False

    @patch("apps.quiz.views.grade_short_answer")
    def test_submit_answer_short_answer(
        self, mock_grade, authenticated_client, quiz
    ):
        """Test submitting a short answer."""
        mock_grade.return_value = (True, "Great answer!")

        question = QuizQuestion.objects.create(
            quiz=quiz,
            question_text="Explain the significance of Nicaea.",
            question_type=QuizQuestion.QuestionType.SHORT_ANSWER,
            correct_answer="It established the Nicene Creed.",
            explanation="The Council produced the Nicene Creed.",
            order=1,
        )

        url = reverse("quiz:quiz-submit-answer", kwargs={"pk": quiz.id})
        data = {
            "question_id": question.id,
            "answer": "The council created the Nicene Creed to address Arianism.",
        }

        response = authenticated_client.post(url, data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["is_correct"] is True
        assert response.data["feedback"] == "Great answer!"
        assert mock_grade.called

    def test_submit_answer_invalid_question(self, authenticated_client, quiz):
        """Test submitting answer for non-existent question."""
        url = reverse("quiz:quiz-submit-answer", kwargs={"pk": quiz.id})
        data = {
            "question_id": 99999,
            "answer": "1",
        }

        response = authenticated_client.post(url, data)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_complete_quiz(self, authenticated_client, quiz, quiz_question):
        """Test completing a quiz."""
        # Answer the question first
        quiz_question.user_answer = "1"
        quiz_question.is_correct = True
        quiz_question.save()

        url = reverse("quiz:quiz-complete", kwargs={"pk": quiz.id})
        response = authenticated_client.post(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["score"] == 1
        assert response.data["total_questions"] == 5
        assert response.data["percentage_score"] == 20
        assert response.data["passed"] is False
        assert response.data["completed_at"] is not None

        # Verify quiz was updated
        quiz.refresh_from_db()
        assert quiz.score == 1
        assert quiz.completed_at is not None

    def test_complete_quiz_already_completed(
        self, authenticated_client, completed_quiz
    ):
        """Test completing an already completed quiz."""
        url = reverse("quiz:quiz-complete", kwargs={"pk": completed_quiz.id})
        response = authenticated_client.post(url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestQuizStatsAPI:
    """Test Quiz Stats API endpoint."""

    def test_quiz_stats(self, authenticated_client, completed_quiz):
        """Test getting quiz statistics."""
        url = reverse("quiz:stats")
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["total_quizzes"] == 1
        assert response.data["total_completed"] == 1
        assert response.data["quizzes_passed"] == 1
        assert len(response.data["by_era"]) == 1
        assert response.data["by_era"][0]["era_name"] == "Early Church"

    def test_quiz_stats_empty(self, authenticated_client):
        """Test stats with no quizzes."""
        url = reverse("quiz:stats")
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["total_quizzes"] == 0
        assert response.data["total_completed"] == 0
        assert response.data["quizzes_passed"] == 0


# =============================================================================
# Service Function Tests
# =============================================================================


@pytest.mark.django_db
class TestQuizServices:
    """Test quiz service functions."""

    @patch("apps.quiz.services.client")
    def test_generate_quiz_questions(self, mock_client, quiz, sample_era):
        """Test quiz question generation."""
        from apps.quiz.services import generate_quiz_questions

        # Mock OpenAI response
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(
                    content='{"questions": [{"question_text": "Test?", "question_type": "mc", "options": ["A", "B", "C", "D"], "correct_answer": "0", "explanation": "Test explanation"}]}'
                )
            )
        ]
        mock_response.usage = MagicMock(prompt_tokens=100, completion_tokens=200)
        mock_client.chat.completions.create.return_value = mock_response

        generate_quiz_questions(quiz)

        # Verify OpenAI was called
        assert mock_client.chat.completions.create.called

        # Verify questions were created
        assert quiz.questions.count() == 1
        question = quiz.questions.first()
        assert question.question_text == "Test?"
        assert question.question_type == "mc"

        # Verify token tracking
        quiz.refresh_from_db()
        assert quiz.generation_input_tokens == 100
        assert quiz.generation_output_tokens == 200

    @patch("apps.quiz.services.client")
    def test_grade_short_answer(self, mock_client):
        """Test short answer grading."""
        from apps.quiz.services import grade_short_answer

        # Mock OpenAI response
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(
                    content='{"is_correct": true, "feedback": "Excellent answer!"}'
                )
            )
        ]
        mock_client.chat.completions.create.return_value = mock_response

        is_correct, feedback = grade_short_answer(
            "What is Nicaea?",
            "The Council of Nicaea established the Nicene Creed.",
            "It created the Nicene Creed to address Arianism.",
        )

        assert is_correct is True
        assert feedback == "Excellent answer!"
        assert mock_client.chat.completions.create.called

    @patch("apps.quiz.services.client")
    def test_grade_short_answer_error(self, mock_client):
        """Test short answer grading with API error."""
        from apps.quiz.services import grade_short_answer

        # Mock OpenAI error
        mock_client.chat.completions.create.side_effect = Exception("API Error")

        is_correct, feedback = grade_short_answer(
            "What is Nicaea?",
            "The Council of Nicaea established the Nicene Creed.",
            "User answer",
        )

        # Should return fallback values
        assert is_correct is False
        assert "couldn't grade" in feedback
