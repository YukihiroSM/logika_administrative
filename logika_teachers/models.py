from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth.models import User


class TeacherProfile(models.Model):
    lms_id = models.CharField(max_length=16)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    related_tutors = models.ManyToManyField("TutorProfile", related_name="related_teachers")
    telegram_nickname = models.CharField(max_length=64, null=True, blank=True)
    phone_number = models.CharField(max_length=16, null=True, blank=True)
    one_c_ids = models.CharField(max_length=64, null=True, blank=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


class TutorProfile(models.Model):
    one_c_name = models.CharField(max_length=64, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="tutor_profile")

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"
