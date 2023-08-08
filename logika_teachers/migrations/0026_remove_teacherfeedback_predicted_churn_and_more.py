# Generated by Django 4.2.3 on 2023-08-08 14:46

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("logika_teachers", "0025_alter_teacherfeedback_predicted_churn"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="teacherfeedback",
            name="predicted_churn",
        ),
        migrations.AddField(
            model_name="teacherfeedback",
            name="predicted_churn_object",
            field=models.BinaryField(blank=True, null=True),
        ),
    ]
