# Generated by Django 4.2.3 on 2023-08-03 20:52

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("logika_teachers", "0019_alter_teacherfeedback_lesson_mark"),
    ]

    operations = [
        migrations.AlterField(
            model_name="teacherfeedback",
            name="additional_problems",
            field=models.CharField(blank=True, max_length=1024, null=True),
        ),
    ]
