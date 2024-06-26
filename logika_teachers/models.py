from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth.models import User
import uuid


class TeacherProfile(models.Model):
    lms_id = models.CharField(max_length=16)
    user = models.ForeignKey(
        User, on_delete=models.DO_NOTHING, related_name="teacher_profile"
    )
    related_tutors = models.ManyToManyField(
        "TutorProfile", related_name="related_teachers"
    )
    telegram_nickname = models.CharField(max_length=64, null=True, blank=True)
    phone_number = models.CharField(max_length=64, null=True, blank=True)
    one_c_ids = models.CharField(max_length=64, null=True, blank=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


class TutorProfile(models.Model):
    one_c_name = models.CharField(max_length=64, null=True, blank=True)
    user = models.ForeignKey(
        User, on_delete=models.DO_NOTHING, related_name="tutor_profile"
    )
    auth_token = models.CharField(max_length=64, null=True, blank=True, default=None)
    login_timestamp = models.DateTimeField(null=True, blank=True, default=None)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

    def get_full_name(self):
        return f"{self.user.last_name} {self.user.first_name}"


class RegionalTutorProfile(models.Model):
    one_c_name = models.CharField(max_length=64, null=True, blank=True)
    user = models.ForeignKey(
        User, on_delete=models.DO_NOTHING, related_name="regional_tutor_profile"
    )
    auth_token = models.CharField(max_length=64, null=True, blank=True, default=None)
    login_timestamp = models.DateTimeField(null=True, blank=True, default=None)
    related_tutors = models.ManyToManyField(
        "TutorProfile", related_name="related_regional_tutors"
    )

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


class TeacherFeedback(models.Model):
    teacher = models.ForeignKey(TeacherProfile, on_delete=models.DO_NOTHING)
    tutor = models.ForeignKey(TutorProfile, on_delete=models.DO_NOTHING)
    lesson_mark = models.IntegerField()
    mistakes = models.TextField()
    problems = ArrayField(models.CharField(max_length=256))
    additional_problems = models.TextField(null=True, blank=True)
    predicted_churn_object = models.BinaryField(null=True, blank=True)
    technical_problems = models.TextField(null=True, blank=True)
    km_work_comment = models.TextField(blank=True, null=True)
    km_work_mark = models.IntegerField(blank=True, null=True, default=10)
    tutor_work_comment = models.TextField(blank=True, null=True)
    tutor_work_mark = models.IntegerField(blank=True, null=True, default=10)
    created_at = models.DateTimeField(auto_now_add=True)
    commented_churn = models.BooleanField(default=False)

    def __str__(self):
        return f"Форма ЗЗ {self.teacher.user.first_name} {self.teacher.user.last_name} {self.created_at}"


class TeacherComment(models.Model):
    teacher = models.ForeignKey(TeacherProfile, on_delete=models.DO_NOTHING)
    tutor = models.ForeignKey(TutorProfile, on_delete=models.DO_NOTHING)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    comment_type = models.CharField(max_length=16)
    feedback = models.ForeignKey(
        TeacherFeedback,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        default=None,
    )
    group_id = models.CharField(max_length=16, null=True, blank=True, default=None)
    churn_id = models.CharField(max_length=16, null=True, blank=True, default=None)

    def __str__(self):
        return f"Коментар {self.teacher.user.first_name} {self.teacher.user.last_name} {self.created_at}"


class TutorMonthReport(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    report_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    teacher = models.ForeignKey("TeacherProfile", on_delete=models.DO_NOTHING)
    churns_percent = models.CharField(max_length=10, null=True, blank=True)
    performance_percent = models.CharField(max_length=10, null=True, blank=True)
    is_salary_counted = models.BooleanField(default=False)
    conversion = models.CharField(max_length=10, null=True, blank=True)
    month = models.CharField(max_length=20, null=True, blank=True)
    tutor = models.ForeignKey("TutorProfile", on_delete=models.DO_NOTHING)
    category = models.CharField(max_length=20, default="B")
