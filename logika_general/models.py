import uuid
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.auth.models import User


class Group(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lms_id = models.IntegerField()
    title = models.CharField(max_length=255)
    venue = models.CharField(max_length=255)
    teacher_name = models.CharField(max_length=255)
    type = models.CharField(max_length=16)
    status = models.CharField(max_length=3)
    client_manager = models.CharField(max_length=255, null=True, blank=True)
    group_start = models.DateField(null=True, default=None)
    group_course = models.CharField(null=True, default=None)
    processing_status = models.CharField(max_length=16, default="new")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title}"


class Notification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=255)
    body = models.TextField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    content_object = GenericForeignKey("content_type", "object_id")
    status = models.CharField(max_length=16, default="new")

    def __str__(self):
        return f"{self.title}"


class Location(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    lms_location_name = models.CharField(max_length=255)
    one_c_location_name = models.CharField(max_length=255)
    status = models.CharField(max_length=16, default="open")

    def __str__(self):
        return f"{self.lms_location_name}"


class ClientManagerProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    auth_token = models.TextField(null=True, blank=True)
    login_timestamp = models.DateTimeField(null=True, default=None)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    related_tms = models.ManyToManyField(
        "TerritorialManagerProfile", related_name="client_managers"
    )

    class Meta:
        ordering = ["user__date_joined"]

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


class TerritorialManagerProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    auth_token = models.TextField(null=True, blank=True)
    login_timestamp = models.DateTimeField(null=True, default=None)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    related_rms = models.ManyToManyField(
        "RegionalManagerProfile", related_name="territorial_managers"
    )

    class Meta:
        ordering = ["user__date_joined"]

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


class RegionalManagerProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    login_timestamp = models.DateTimeField(null=True, default=None)
    auth_token = models.TextField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)

    class Meta:
        ordering = ["user__date_joined"]

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"
