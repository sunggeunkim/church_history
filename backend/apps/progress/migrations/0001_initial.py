# Generated migration for progress models

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('eras', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Achievement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(max_length=100, unique=True)),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('category', models.CharField(choices=[('exploration', 'Exploration'), ('chat', 'Chat'), ('quiz', 'Quiz'), ('streak', 'Streak'), ('mastery', 'Mastery')], max_length=20)),
                ('icon_key', models.CharField(help_text="Lucide icon name (e.g., 'trophy', 'star', 'target')", max_length=50)),
                ('order', models.PositiveIntegerField(default=0, help_text='Display order within category')),
            ],
            options={
                'ordering': ['category', 'order'],
            },
        ),
        migrations.CreateModel(
            name='UserProgress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('era_visited', models.BooleanField(default=False, help_text='True if user has expanded this era on canvas')),
                ('first_visited_at', models.DateTimeField(blank=True, help_text='First time user expanded this era', null=True)),
                ('chat_sessions_count', models.PositiveIntegerField(default=0, help_text='Number of chat sessions for this era')),
                ('last_chat_at', models.DateTimeField(blank=True, help_text='Most recent chat session for this era', null=True)),
                ('quizzes_completed', models.PositiveIntegerField(default=0, help_text='Number of completed quizzes for this era')),
                ('quizzes_passed', models.PositiveIntegerField(default=0, help_text='Number of quizzes passed (70%+) for this era')),
                ('best_quiz_score', models.PositiveIntegerField(blank=True, help_text='Best percentage score achieved for this era', null=True)),
                ('last_quiz_at', models.DateTimeField(blank=True, help_text='Most recent quiz completion for this era', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('era', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_progress', to='eras.era')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='era_progress', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['era__order'],
            },
        ),
        migrations.CreateModel(
            name='UserAchievement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unlocked_at', models.DateTimeField(auto_now_add=True)),
                ('achievement', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_achievements', to='progress.achievement')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='achievements', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-unlocked_at'],
            },
        ),
        migrations.AddConstraint(
            model_name='userprogress',
            constraint=models.UniqueConstraint(fields=('user', 'era'), name='progress_userprogress_user_era_uniq'),
        ),
        migrations.AddIndex(
            model_name='userprogress',
            index=models.Index(fields=['user', 'updated_at'], name='progress_us_user_id_6d7e8f_idx'),
        ),
        migrations.AddConstraint(
            model_name='userachievement',
            constraint=models.UniqueConstraint(fields=('user', 'achievement'), name='progress_userachievement_user_achievement_uniq'),
        ),
        migrations.AddIndex(
            model_name='userachievement',
            index=models.Index(fields=['user', '-unlocked_at'], name='progress_us_user_id_9a0b1c_idx'),
        ),
    ]
