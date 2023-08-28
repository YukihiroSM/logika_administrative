from django.db import models
from django.contrib.auth.models import User


class ClientManagerProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    related_regional_manager = models.ManyToManyField("RegionalManagerProfile", blank=True, related_name="related_client_managers")
    related_territorial_manager = models.ManyToManyField("TerritorialManagerProfile", blank=True, related_name="related_client_managers")
    auth_token = models.CharField(max_length=64, null=True, blank=True, default=None)
    login_timestamp = models.DateTimeField(null=True, blank=True, default=None)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


class RegionalManagerProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    auth_token = models.CharField(max_length=64, null=True, blank=True, default=None)
    login_timestamp = models.DateTimeField(null=True, blank=True, default=None)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


class TerritorialManagerProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    related_regional_manager = models.ManyToManyField("RegionalManagerProfile", blank=True, related_name="related_territorial_managers")
    auth_token = models.CharField(max_length=64, null=True, blank=True, default=None)
    login_timestamp = models.DateTimeField(null=True, blank=True, default=None)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"