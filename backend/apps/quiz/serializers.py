"""Serializers for quiz app API endpoints."""

from rest_framework import serializers

from .models import Quiz, QuizQuestion


class QuizQuestionSerializer(serializers.ModelSerializer):
    """Serializer for QuizQuestion (in-progress quiz, no correct answer shown)."""

    class Meta:
        model = QuizQuestion
        fields = [
            "id",
            "question_text",
            "question_type",
            "options",
            "order",
        ]
        read_only_fields = ["id"]


class QuizQuestionDetailSerializer(serializers.ModelSerializer):
    """Serializer for QuizQuestion with full details (for completed quizzes)."""

    class Meta:
        model = QuizQuestion
        fields = [
            "id",
            "question_text",
            "question_type",
            "options",
            "user_answer",
            "correct_answer",
            "is_correct",
            "explanation",
            "feedback",
            "order",
        ]
        read_only_fields = ["id"]


class QuizListSerializer(serializers.ModelSerializer):
    """Serializer for Quiz list view (no questions embedded)."""

    era_name = serializers.CharField(source="era.name", read_only=True, default=None)
    percentage_score = serializers.IntegerField(read_only=True)
    passed = serializers.BooleanField(read_only=True)

    class Meta:
        model = Quiz
        fields = [
            "id",
            "era",
            "era_name",
            "difficulty",
            "score",
            "total_questions",
            "percentage_score",
            "passed",
            "completed_at",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "score",
            "completed_at",
            "created_at",
        ]


class QuizSerializer(serializers.ModelSerializer):
    """Serializer for Quiz detail view with questions.

    Uses conditional serializer for questions based on quiz completion status.
    In-progress quizzes don't show correct answers; completed quizzes show full details.
    """

    era_name = serializers.CharField(source="era.name", read_only=True, default=None)
    percentage_score = serializers.IntegerField(read_only=True)
    passed = serializers.BooleanField(read_only=True)
    questions = serializers.SerializerMethodField()

    class Meta:
        model = Quiz
        fields = [
            "id",
            "era",
            "era_name",
            "difficulty",
            "score",
            "total_questions",
            "percentage_score",
            "passed",
            "completed_at",
            "created_at",
            "questions",
        ]
        read_only_fields = [
            "id",
            "score",
            "completed_at",
            "created_at",
        ]

    def get_questions(self, obj):
        """Return questions with appropriate serializer based on completion status."""
        if obj.is_completed:
            serializer = QuizQuestionDetailSerializer(obj.questions.all(), many=True)
        else:
            serializer = QuizQuestionSerializer(obj.questions.all(), many=True)
        return serializer.data


class QuizCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new quiz."""

    era_id = serializers.IntegerField(required=False, allow_null=True, source="era.id")
    question_count = serializers.IntegerField(min_value=5, max_value=10, write_only=True)

    class Meta:
        model = Quiz
        fields = [
            "id",
            "era_id",
            "difficulty",
            "question_count",
        ]
        read_only_fields = ["id"]

    def validate_era_id(self, value):
        """Validate that the era exists if provided."""
        if value is not None:
            from apps.eras.models import Era

            if not Era.objects.filter(id=value).exists():
                raise serializers.ValidationError("Era not found.")
        return value

    def create(self, validated_data):
        """Create quiz with total_questions set from question_count."""
        question_count = validated_data.pop("question_count")
        era_data = validated_data.pop("era", None)

        quiz = Quiz.objects.create(
            **validated_data,
            era_id=era_data.get("id") if era_data else None,
            total_questions=question_count,
        )
        return quiz


class QuizAnswerSerializer(serializers.Serializer):
    """Serializer for submitting an answer to a question."""

    question_id = serializers.IntegerField()
    answer = serializers.CharField()
