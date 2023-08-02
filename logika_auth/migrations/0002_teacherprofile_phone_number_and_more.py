# Generated by Django 4.2.3 on 2023-08-01 19:18

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("logika_auth", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="teacherprofile",
            name="phone_number",
            field=models.CharField(blank=True, max_length=16, null=True),
        ),
        migrations.AddField(
            model_name="teacherprofile",
            name="telegram_nickname",
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
    ]