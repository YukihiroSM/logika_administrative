# Generated by Django 4.2.3 on 2023-08-30 14:12

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    dependencies = [
        ("logika_teachers", "0029_alter_teachercomment_comment_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="TutorMonthReport",
            fields=[
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(blank=True, null=True)),
                (
                    "report_id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "churns_percent",
                    models.CharField(blank=True, max_length=10, null=True),
                ),
                (
                    "performance_percent",
                    models.CharField(blank=True, max_length=10, null=True),
                ),
                ("is_salary_counted", models.BooleanField(default=False)),
                ("conversion", models.CharField(blank=True, max_length=10, null=True)),
                (
                    "teacher",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to="logika_teachers.teacherprofile",
                    ),
                ),
            ],
        ),
    ]
