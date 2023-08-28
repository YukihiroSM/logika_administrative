# Generated by Django 4.2.3 on 2023-08-21 17:42

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="RegionalManagerProfile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "auth_token",
                    models.CharField(
                        blank=True, default=None, max_length=64, null=True
                    ),
                ),
                (
                    "login_timestamp",
                    models.DateTimeField(blank=True, default=None, null=True),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="TerritorialManagerProfile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "auth_token",
                    models.CharField(
                        blank=True, default=None, max_length=64, null=True
                    ),
                ),
                (
                    "login_timestamp",
                    models.DateTimeField(blank=True, default=None, null=True),
                ),
                (
                    "related_regional_manager",
                    models.ManyToManyField(
                        blank=True,
                        related_name="related_territorial_managers",
                        to="logika_analytics.regionalmanagerprofile",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ClientManagerProfile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "auth_token",
                    models.CharField(
                        blank=True, default=None, max_length=64, null=True
                    ),
                ),
                (
                    "login_timestamp",
                    models.DateTimeField(blank=True, default=None, null=True),
                ),
                (
                    "related_regional_manager",
                    models.ManyToManyField(
                        blank=True,
                        related_name="related_client_managers",
                        to="logika_analytics.regionalmanagerprofile",
                    ),
                ),
                (
                    "related_territorial_manager",
                    models.ManyToManyField(
                        blank=True,
                        related_name="related_client_managers",
                        to="logika_analytics.territorialmanagerprofile",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]