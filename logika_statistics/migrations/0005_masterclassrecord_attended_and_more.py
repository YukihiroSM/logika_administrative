# Generated by Django 4.2.3 on 2023-12-16 16:00

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("logika_statistics", "0004_masterclassrecord"),
    ]

    operations = [
        migrations.AddField(
            model_name="masterclassrecord",
            name="attended",
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="masterclassrecord",
            name="course_id",
            field=models.CharField(max_length=16, null=True),
        ),
        migrations.AddField(
            model_name="masterclassrecord",
            name="course_title",
            field=models.CharField(max_length=128, null=True),
        ),
        migrations.AddField(
            model_name="masterclassrecord",
            name="enrolled",
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="masterclassrecord",
            name="teacher_lms_id",
            field=models.CharField(max_length=16, null=True),
        ),
        migrations.AlterField(
            model_name="masterclassrecord",
            name="business",
            field=models.CharField(
                choices=[("programming", "Програмування"), ("english", "Англійська")],
                max_length=16,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="masterclassrecord",
            name="client_manager",
            field=models.CharField(max_length=128, null=True),
        ),
        migrations.AlterField(
            model_name="masterclassrecord",
            name="location",
            field=models.CharField(max_length=128, null=True),
        ),
        migrations.AlterField(
            model_name="masterclassrecord",
            name="regional_manager",
            field=models.CharField(max_length=128, null=True),
        ),
        migrations.AlterField(
            model_name="masterclassrecord",
            name="teacher",
            field=models.CharField(max_length=128, null=True),
        ),
        migrations.AlterField(
            model_name="masterclassrecord",
            name="territorial_manager",
            field=models.CharField(max_length=128, null=True),
        ),
        migrations.AlterField(
            model_name="masterclassrecord",
            name="tutor",
            field=models.CharField(max_length=128, null=True),
        ),
    ]
