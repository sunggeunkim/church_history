# Generated migration for quiz models

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
            name='Quiz',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('difficulty', models.CharField(choices=[('beginner', 'Beginner'), ('intermediate', 'Intermediate'), ('advanced', 'Advanced')], default='beginner', max_length=20)),
                ('score', models.PositiveIntegerField(default=0, help_text='Number of correct answers')),
                ('total_questions', models.PositiveIntegerField(default=0)),
                ('completed_at', models.DateTimeField(blank=True, help_text='Null if quiz is in progress', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('generation_input_tokens', models.PositiveIntegerField(default=0)),
                ('generation_output_tokens', models.PositiveIntegerField(default=0)),
                ('grading_input_tokens', models.PositiveIntegerField(default=0)),
                ('grading_output_tokens', models.PositiveIntegerField(default=0)),
                ('era', models.ForeignKey(blank=True, help_text="Null for 'All Eras' quizzes", null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='quizzes', to='eras.era')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='quizzes', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='QuizQuestion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_text', models.TextField()),
                ('question_type', models.CharField(choices=[('mc', 'Multiple Choice'), ('tf', 'True/False'), ('sa', 'Short Answer')], max_length=2)),
                ('options', models.JSONField(blank=True, default=list, help_text="Array of options for MC questions; ['True', 'False'] for TF; empty for SA")),
                ('correct_answer', models.TextField(help_text='Index (as string) for MC/TF, or reference answer text for SA')),
                ('user_answer', models.TextField(blank=True, help_text="Index (as string) for MC/TF, or user's text for SA")),
                ('is_correct', models.BooleanField(blank=True, help_text='Null if not yet answered', null=True)),
                ('explanation', models.TextField(blank=True, help_text='Explanation of the correct answer (AI-generated)')),
                ('feedback', models.TextField(blank=True, help_text='Personalized feedback for SA questions (AI-generated)')),
                ('order', models.PositiveIntegerField(help_text='Question order within the quiz')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('quiz', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='quiz.quiz')),
            ],
            options={
                'ordering': ['quiz', 'order'],
            },
        ),
        migrations.AddIndex(
            model_name='quiz',
            index=models.Index(fields=['user', '-created_at'], name='quiz_quiz_user_id_8f6e2a_idx'),
        ),
        migrations.AddIndex(
            model_name='quiz',
            index=models.Index(fields=['user', 'era'], name='quiz_quiz_user_id_0be3f4_idx'),
        ),
        migrations.AddIndex(
            model_name='quizquestion',
            index=models.Index(fields=['quiz', 'order'], name='quiz_quizqu_quiz_id_40d4f3_idx'),
        ),
    ]
