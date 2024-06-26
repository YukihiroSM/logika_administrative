# Generated by Django 4.2.3 on 2023-08-02 21:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("logika_teachers", "0012_tutorprofile_login_timestamp"),
    ]

    operations = [
        migrations.AddField(
            model_name="teachercomment",
            name="group_id",
            field=models.CharField(blank=True, default=None, max_length=16, null=True),
        ),
        migrations.AlterField(
            model_name="teachercomment",
            name="feedback",
            field=models.ForeignKey(
                blank=True,
                default=None,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                to="logika_teachers.teacherfeedback",
            ),
        ),
    ]
