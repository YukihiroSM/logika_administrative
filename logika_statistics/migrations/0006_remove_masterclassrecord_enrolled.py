# Generated by Django 4.2.3 on 2023-12-16 16:10

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("logika_statistics", "0005_masterclassrecord_attended_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="masterclassrecord",
            name="enrolled",
        ),
    ]
