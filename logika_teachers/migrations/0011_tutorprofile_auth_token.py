# Generated by Django 4.2.3 on 2023-08-02 20:23

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("logika_teachers", "0010_teachercomment"),
    ]

    operations = [
        migrations.AddField(
            model_name="tutorprofile",
            name="auth_token",
            field=models.CharField(blank=True, default=None, max_length=64, null=True),
        ),
    ]
