from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth.models import User


class TeacherProfile(models.Model):
    lms_id = models.CharField(max_length=16)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    related_tutors = models.ManyToManyField("TutorProfile", related_name="related_teachers")
    telegram_nickname = models.CharField(max_length=64, null=True, blank=True)
    phone_number = models.CharField(max_length=64, null=True, blank=True)
    one_c_ids = models.CharField(max_length=64, null=True, blank=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


class TutorProfile(models.Model):
    one_c_name = models.CharField(max_length=64, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="tutor_profile")
    auth_token = models.CharField(max_length=64, null=True, blank=True, default=None)
    login_timestamp = models.DateTimeField(null=True, blank=True, default=None)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


class TeacherFeedback(models.Model):
    teacher = models.ForeignKey(TeacherProfile, on_delete=models.DO_NOTHING)
    tutor = models.ForeignKey(TutorProfile, on_delete=models.DO_NOTHING)
    lesson_mark = models.IntegerField()
    mistakes = models.CharField(max_length=256)
    problems = ArrayField(models.CharField(max_length=256))
    additional_problems = models.CharField(max_length=1024)
    predicted_churn = models.CharField(max_length=256)
    technical_problems = models.CharField(max_length=1024)
    km_work_comment = models.CharField(max_length=1024, blank=True, null=True)
    tutor_work_comment = models.CharField(max_length=1024, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Форма ЗЗ {self.teacher.user.first_name} {self.teacher.user.last_name} {self.created_at}"


class TeacherComment(models.Model):
    teacher = models.ForeignKey(TeacherProfile, on_delete=models.DO_NOTHING)
    tutor = models.ForeignKey(TutorProfile, on_delete=models.DO_NOTHING)
    comment = models.CharField(max_length=1024)
    created_at = models.DateTimeField(auto_now_add=True)
    comment_type = models.CharField(max_length=16)
    feedback = models.ForeignKey(TeacherFeedback, on_delete=models.DO_NOTHING, null=True, blank=True, default=None)
    group_id = models.CharField(max_length=16, null=True, blank=True, default=None)

    def __str__(self):
        return f"Коментар {self.teacher.user.first_name} {self.teacher.user.last_name} {self.created_at}"

