# Generated by Django 4.2.3 on 2023-11-16 20:55

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("logika_general", "0008_clientmanagerprofile_login_timestamp_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="clientmanagerprofile",
            options={"ordering": ["user__date_joined"]},
        ),
        migrations.AlterModelOptions(
            name="regionalmanagerprofile",
            options={"ordering": ["user__date_joined"]},
        ),
        migrations.AlterModelOptions(
            name="territorialmanagerprofile",
            options={"ordering": ["user__date_joined"]},
        ),
    ]
