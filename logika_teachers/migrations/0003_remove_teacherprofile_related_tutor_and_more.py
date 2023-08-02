# Generated by Django 4.2.3 on 2023-08-02 11:40

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("logika_teachers", "0002_remove_teacherprofile_one_c_ids_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="teacherprofile",
            name="related_tutor",
        ),
        migrations.AddField(
            model_name="teacherprofile",
            name="related_tutors",
            field=models.ManyToManyField(
                related_name="related_teachers", to="logika_teachers.tutorprofile"
            ),
        ),
    ]