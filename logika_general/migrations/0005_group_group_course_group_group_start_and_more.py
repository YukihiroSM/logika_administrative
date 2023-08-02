# Generated by Django 4.2.3 on 2023-07-29 12:10

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("logika_general", "0004_alter_group_client_manager"),
    ]

    operations = [
        migrations.AddField(
            model_name="group",
            name="group_course",
            field=models.CharField(default=None, null=True),
        ),
        migrations.AddField(
            model_name="group",
            name="group_start",
            field=models.DateField(default=None, null=True),
        ),
        migrations.AddField(
            model_name="group",
            name="processing_status",
            field=models.CharField(default="new", max_length=16),
        ),
    ]
