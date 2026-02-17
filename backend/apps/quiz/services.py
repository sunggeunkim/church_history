"""Quiz generation and grading services using OpenAI.

Provides functions for generating quiz questions based on era content
and grading short answer questions using AI.
"""

import json
import logging
from typing import Any

import openai
from django.conf import settings

from apps.eras.models import Era

from .models import Quiz, QuizQuestion

logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)


def generate_quiz_questions(quiz: Quiz) -> None:
    """Generate quiz questions using OpenAI GPT-4o.

    Creates QuizQuestion instances for the given quiz based on:
    - Quiz era (or all eras if era=null)
    - Quiz difficulty
    - Era content (description, key events, key figures)

    Args:
        quiz: The Quiz instance to generate questions for.

    Raises:
        openai.APIError: If OpenAI API call fails.
    """
    # Gather era content
    if quiz.era:
        era_context = _build_era_context(quiz.era)
        scope = f"the {quiz.era.name} era ({quiz.era.start_year}-{quiz.era.end_year or 'present'})"
    else:
        # "All Eras" quiz
        eras = Era.objects.all().prefetch_related("key_events", "key_figures")
        era_context = "\n\n".join([_build_era_context(era) for era in eras])
        scope = "all eras of church history"

    # Build prompt
    prompt = _build_generation_prompt(
        era_context=era_context,
        scope=scope,
        difficulty=quiz.difficulty,
        question_count=quiz.total_questions,
    )

    try:
        # Call OpenAI
        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are a church history quiz generator. Generate questions in valid JSON format.",
                },
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
            max_tokens=3000,
        )

        # Track tokens
        quiz.generation_input_tokens = response.usage.prompt_tokens
        quiz.generation_output_tokens = response.usage.completion_tokens
        quiz.save(update_fields=["generation_input_tokens", "generation_output_tokens"])

        # Parse response
        questions_data = json.loads(response.choices[0].message.content)

        # Create QuizQuestion instances
        _create_quiz_questions(quiz, questions_data["questions"])

    except openai.APIError as e:
        logger.exception("OpenAI API error during quiz generation: %s", e)
        raise
    except json.JSONDecodeError as e:
        logger.exception("Failed to parse OpenAI JSON response: %s", e)
        raise
    except KeyError as e:
        logger.exception("Unexpected OpenAI response structure: %s", e)
        raise


def _build_era_context(era: Era) -> str:
    """Build context text for an era."""
    context_parts = [
        f"Era: {era.name} ({era.start_year}-{era.end_year or 'present'})",
        f"Description: {era.description}",
        "",
        "Key Events:",
    ]

    for event in era.key_events.all()[:10]:  # Limit to 10 events
        context_parts.append(f"- {event.year}: {event.title}")
        if event.description:
            context_parts.append(f"  {event.description[:200]}")

    context_parts.extend(["", "Key Figures:"])
    for figure in era.key_figures.all()[:10]:  # Limit to 10 figures
        years = ""
        if figure.birth_year and figure.death_year:
            years = f" ({figure.birth_year}-{figure.death_year})"
        context_parts.append(f"- {figure.name}{years}: {figure.title}")
        if figure.description:
            context_parts.append(f"  {figure.description[:200]}")

    return "\n".join(context_parts)


def _build_generation_prompt(
    era_context: str,
    scope: str,
    difficulty: str,
    question_count: int,
) -> str:
    """Build the prompt for quiz generation."""
    return f"""Generate a church history quiz with {question_count} questions about {scope}.

**Difficulty Level:** {difficulty}
- Beginner: Basic facts, key dates, major figures
- Intermediate: Conceptual understanding, cause-effect, significance
- Advanced: Analysis, comparison, theological nuance

**Question Type Distribution:**
- {question_count - 2} multiple choice questions (4 options each)
- 1 true/false question
- 1 short answer question

**Era Content:**
{era_context}

**Output Format (JSON):**
{{
  "questions": [
    {{
      "question_text": "What year was the Council of Nicaea?",
      "question_type": "mc",
      "options": ["313", "325", "381", "451"],
      "correct_answer": "1",
      "explanation": "The Council of Nicaea convened in 325 AD..."
    }},
    {{
      "question_text": "Augustine was the Bishop of Hippo.",
      "question_type": "tf",
      "options": ["True", "False"],
      "correct_answer": "0",
      "explanation": "Augustine served as Bishop of Hippo from 395-430 AD..."
    }},
    {{
      "question_text": "Explain the significance of the Edict of Milan.",
      "question_type": "sa",
      "options": [],
      "correct_answer": "The Edict of Milan (313 AD) legalized Christianity in the Roman Empire, ending persecution and marking a turning point...",
      "explanation": "A complete answer should mention: legalization of Christianity, end of persecution, Emperor Constantine, turning point for church growth."
    }}
  ]
}}

**Requirements:**
- Use historically accurate information from the era content provided
- Ensure all multiple choice questions have exactly 4 options
- For MC questions, correct_answer is the index (0-3) as a string
- For TF questions, correct_answer is "0" (True) or "1" (False)
- For SA questions, correct_answer is a reference answer (2-3 sentences)
- Each question must have a detailed explanation (2-3 sentences)
- Vary difficulty appropriately for the {difficulty} level
- Ensure questions are clear, unambiguous, and educational

Generate the quiz now in valid JSON format:"""


def _create_quiz_questions(quiz: Quiz, questions_data: list[dict[str, Any]]) -> None:
    """Create QuizQuestion instances from parsed JSON."""
    question_instances = []

    for i, q_data in enumerate(questions_data):
        question_instances.append(
            QuizQuestion(
                quiz=quiz,
                question_text=q_data["question_text"],
                question_type=q_data["question_type"],
                options=q_data.get("options", []),
                correct_answer=q_data["correct_answer"],
                explanation=q_data["explanation"],
                order=i + 1,
            )
        )

    QuizQuestion.objects.bulk_create(question_instances)


def grade_short_answer(
    question_text: str,
    correct_answer: str,
    user_answer: str,
) -> tuple[bool, str]:
    """Grade a short answer question using OpenAI.

    Args:
        question_text: The question text.
        correct_answer: The reference answer.
        user_answer: The user's submitted answer.

    Returns:
        Tuple of (is_correct, feedback).
    """
    prompt = f"""Grade this short answer question:

**Question:** {question_text}

**Reference Answer:** {correct_answer}

**Student Answer:** {user_answer}

**Instructions:**
- Evaluate if the student's answer is correct (substantially matches the reference answer)
- Be lenient with wording differences
- Focus on key concepts, not exact phrasing
- Provide constructive feedback (1-2 sentences)

**Output Format (JSON):**
{{
  "is_correct": true,
  "feedback": "Excellent! You correctly identified the key significance of the Edict of Milan."
}}

or

{{
  "is_correct": false,
  "feedback": "Your answer misses the key point about legalization. The Edict of Milan legalized Christianity, ending persecution."
}}

Grade the answer now in valid JSON format:"""

    try:
        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are a church history teaching assistant grading student answers.",
                },
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.3,  # Lower temperature for consistent grading
            max_tokens=200,
        )

        result = json.loads(response.choices[0].message.content)
        return result["is_correct"], result["feedback"]

    except Exception as e:
        logger.exception("OpenAI API error during short answer grading: %s", e)
        # Fallback: mark as incorrect with generic feedback
        return (
            False,
            "We couldn't grade your answer automatically. Please review the reference answer.",
        )
