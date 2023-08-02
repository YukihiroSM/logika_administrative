from django import forms
from django.contrib.postgres.forms import SimpleArrayField


class TeacherCreateForm(forms.Form):
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    email = forms.EmailField()
    phone_number = forms.CharField(max_length=15)
    lms_id = forms.CharField(max_length=16)
    telegram_nickname = forms.CharField(max_length=64, required=False)
    one_c_ids = forms.CharField(max_length=64)


PROBLEMS_CHOICES = (
    ("Не маєте авторитету перед учнями", "Не маєте авторитету перед учнями"),
    ("Учні не товаришують один з одним", "Учні не товаришують один з одним"),
    ("Не виконують ДЗ", "Не виконують ДЗ"),
    ("Не активні учні", "Не активні учні"),
    ("Занадто активні учні", "Занадто активні учні"),
    ("Учні не слухаються", "Учні не слухаються"),
    ("В моїх групах немає проблем", "В моїх групах немає проблем"),
)


class TeacherFeedbackForm(forms.Form):
    # lesson_mark = forms.IntegerField(min_value=1, max_value=10, required=True)
    mistakes = forms.CharField(max_length=256, required=True)
    problems = forms.MultipleChoiceField(choices=PROBLEMS_CHOICES, required=True)
    additional_problems = forms.CharField(max_length=1024)
    predicted_churn = forms.CharField(max_length=256, required=True)
    technical_problems = forms.CharField(max_length=1024, required=True)
    km_work_comment = forms.CharField(max_length=1024)
    tutor_work_comment = forms.CharField(max_length=1024)


class TeacherCommentForm(forms.Form):
    comment = forms.CharField(max_length=1024, required=True)
    group_id = forms.CharField(max_length=16)
