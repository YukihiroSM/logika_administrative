# Generated by Django 4.2.3 on 2023-08-08 15:14

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("logika_teachers", "0027_teachercomment_churn_id"),
    ]

    operations = [
        migrations.AddField(
            model_name="teacherfeedback",
            name="commented_churn",
            field=models.BooleanField(default=False),
        ),
    ]
