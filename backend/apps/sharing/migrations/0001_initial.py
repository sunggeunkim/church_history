# Generated migration for ShareLink model

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="ShareLink",
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
                    "token",
                    models.CharField(
                        db_index=True,
                        max_length=16,
                        unique=True,
                    ),
                ),
                (
                    "share_type",
                    models.CharField(
                        choices=[
                            ("achievement", "Achievement"),
                            ("quiz_result", "Quiz Result"),
                            ("progress", "Progress Summary"),
                        ],
                        max_length=20,
                    ),
                ),
                ("content_snapshot", models.JSONField()),
                ("sharer_display_name", models.CharField(max_length=255)),
                ("is_active", models.BooleanField(default=True)),
                ("view_count", models.PositiveIntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="share_links",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="sharelink",
            index=models.Index(
                fields=["user", "-created_at"],
                name="sharing_sh_user_id_a1b2c3_idx",
            ),
        ),
    ]
