# Migration to seed predefined achievements

from django.db import migrations


def create_achievements(apps, schema_editor):
    Achievement = apps.get_model("progress", "Achievement")

    achievements = [
        # Exploration
        {
            "slug": "first-visit",
            "name": "First Steps",
            "description": "Explore your first era on the canvas",
            "category": "exploration",
            "icon_key": "map",
            "order": 1,
        },
        {
            "slug": "all-eras-visited",
            "name": "Time Traveler",
            "description": "Visit all 6 eras on the canvas",
            "category": "exploration",
            "icon_key": "compass",
            "order": 2,
        },

        # Chat
        {
            "slug": "first-chat",
            "name": "Conversation Starter",
            "description": "Start your first chat session",
            "category": "chat",
            "icon_key": "message-circle",
            "order": 1,
        },
        {
            "slug": "chat-all-eras",
            "name": "Curious Mind",
            "description": "Chat about all 6 eras",
            "category": "chat",
            "icon_key": "messages-square",
            "order": 2,
        },
        {
            "slug": "chat-enthusiast",
            "name": "Deep Thinker",
            "description": "Create 10 chat sessions",
            "category": "chat",
            "icon_key": "brain",
            "order": 3,
        },

        # Quiz
        {
            "slug": "first-quiz",
            "name": "Quiz Beginner",
            "description": "Complete your first quiz",
            "category": "quiz",
            "icon_key": "trophy",
            "order": 1,
        },
        {
            "slug": "quiz-all-eras",
            "name": "Well-Rounded Scholar",
            "description": "Pass a quiz in all 6 eras",
            "category": "quiz",
            "icon_key": "graduation-cap",
            "order": 2,
        },
        {
            "slug": "perfect-score",
            "name": "Perfect Scholar",
            "description": "Score 100% on any quiz",
            "category": "quiz",
            "icon_key": "star",
            "order": 3,
        },
        {
            "slug": "quiz-master",
            "name": "Quiz Master",
            "description": "Complete 20 quizzes",
            "category": "quiz",
            "icon_key": "award",
            "order": 4,
        },
        {
            "slug": "high-achiever",
            "name": "High Achiever",
            "description": "Maintain an 85% average across all quizzes",
            "category": "quiz",
            "icon_key": "target",
            "order": 5,
        },

        # Streak
        {
            "slug": "three-day-streak",
            "name": "Consistent Learner",
            "description": "Maintain a 3-day learning streak",
            "category": "streak",
            "icon_key": "flame",
            "order": 1,
        },
        {
            "slug": "seven-day-streak",
            "name": "Dedicated Student",
            "description": "Maintain a 7-day learning streak",
            "category": "streak",
            "icon_key": "zap",
            "order": 2,
        },

        # Mastery
        {
            "slug": "complete-beginner",
            "name": "Complete Explorer",
            "description": "Visit, chat, and pass a quiz in all 6 eras",
            "category": "mastery",
            "icon_key": "crown",
            "order": 1,
        },
    ]

    for data in achievements:
        Achievement.objects.create(**data)


class Migration(migrations.Migration):
    dependencies = [
        ("progress", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_achievements, migrations.RunPython.noop),
    ]
