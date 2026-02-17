# Generated manually for chat app initial models

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("eras", "0001_initial"),
        ("content", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="ChatSession",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(default="New Chat", max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_archived", models.BooleanField(default=False)),
                (
                    "total_input_tokens",
                    models.PositiveIntegerField(default=0),
                ),
                (
                    "total_output_tokens",
                    models.PositiveIntegerField(default=0),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="chat_sessions",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "era",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="chat_sessions",
                        to="eras.era",
                    ),
                ),
            ],
            options={
                "ordering": ["-updated_at"],
            },
        ),
        migrations.CreateModel(
            name="ChatMessage",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "role",
                    models.CharField(
                        choices=[("user", "User"), ("assistant", "Assistant")],
                        max_length=10,
                    ),
                ),
                ("content", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("model_used", models.CharField(blank=True, max_length=50)),
                ("input_tokens", models.PositiveIntegerField(default=0)),
                ("output_tokens", models.PositiveIntegerField(default=0)),
                (
                    "session",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="messages",
                        to="chat.chatsession",
                    ),
                ),
                (
                    "retrieved_chunks",
                    models.ManyToManyField(
                        blank=True,
                        related_name="chat_messages",
                        to="content.contentchunk",
                    ),
                ),
            ],
            options={
                "ordering": ["created_at"],
            },
        ),
        migrations.CreateModel(
            name="MessageCitation",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=500)),
                ("url", models.URLField(blank=True, max_length=500)),
                ("source_name", models.CharField(max_length=255)),
                ("order", models.PositiveIntegerField(default=0)),
                (
                    "message",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="citations",
                        to="chat.chatmessage",
                    ),
                ),
                (
                    "content_item",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="content.contentitem",
                    ),
                ),
            ],
            options={
                "ordering": ["order"],
            },
        ),
        # Indexes for ChatSession
        migrations.AddIndex(
            model_name="chatsession",
            index=models.Index(
                fields=["-updated_at"],
                name="chat_chatses_updated_7b3e4f_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="chatsession",
            index=models.Index(
                fields=["user", "-updated_at"],
                name="chat_chatses_user_id_a1c2d3_idx",
            ),
        ),
        # Indexes for ChatMessage
        migrations.AddIndex(
            model_name="chatmessage",
            index=models.Index(
                fields=["session", "created_at"],
                name="chat_chatmes_session_b4e5f6_idx",
            ),
        ),
        # Indexes for MessageCitation
        migrations.AddIndex(
            model_name="messagecitation",
            index=models.Index(
                fields=["message", "order"],
                name="chat_message_message_c7d8e9_idx",
            ),
        ),
    ]
