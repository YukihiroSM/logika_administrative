# Generated by Django 4.2.3 on 2023-08-08 15:10

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("logika_teachers", "0026_remove_teacherfeedback_predicted_churn_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="teachercomment",
            name="churn_id",
            field=models.CharField(blank=True, default=None, max_length=16, null=True),
        ),
    ]