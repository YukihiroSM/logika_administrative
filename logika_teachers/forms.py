from django import forms
from django.contrib.postgres.forms import SimpleArrayField
from logika_teachers.models import TeacherProfile


class TeacherCreateForm(forms.Form):
    first_name = forms.CharField(max_length=30, label="Ім'я")
    last_name = forms.CharField(max_length=30, label="Прізвище")
    email = forms.EmailField(label="Електронна пошта")
    phone_number = forms.CharField(max_length=64, label="Номер телефону")
    lms_id = forms.CharField(max_length=16, label="ID в LMS")
    telegram_nickname = forms.CharField(max_length=64, required=False, label="Нікнейм в Telegram")
    one_c_ids = forms.CharField(max_length=64, label="ID в 1С")


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
    lesson_mark = forms.IntegerField(min_value=1, max_value=10, required=True, label="Оцінка уроку")
    mistakes = forms.CharField(max_length=256, required=True, label="Помилки")
    problems = forms.MultipleChoiceField(choices=PROBLEMS_CHOICES, required=True, label="Проблеми")
    additional_problems = forms.CharField(max_length=1024, label="Додаткові проблеми", required=False)
    technical_problems = forms.CharField(max_length=1024, required=False, label="Технічні проблеми")
    km_work_mark = forms.IntegerField(min_value=1, max_value=10, required=True, label="Оцінка роботи КМ")
    km_work_comment = forms.CharField(max_length=1024, required=False, label="Коментарі до роботи КМ")
    tutor_work_mark = forms.IntegerField(min_value=1, max_value=10, required=True, label="Оцінка роботи тьютора")
    tutor_work_comment = forms.CharField(max_length=1024, required=False, label="Коментарі до роботи тьютора")


class TeacherCommentForm(forms.Form):
    comment = forms.CharField(max_length=1024, required=True)
    group_id = forms.CharField(max_length=16)


class TeacherPerformanceForm(forms.Form):
    month = forms.CharField(max_length=1024, required=True)
    locations = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
    )


class TeacherEditProfileForm(forms.Form):
    first_name = forms.CharField(max_length=30, label="Ім'я")
    last_name = forms.CharField(max_length=30, label="Прізвище")
    phone_number = forms.CharField(max_length=64, label="Номер телефону")
    lms_id = forms.CharField(max_length=16, label="ID в LMS")
    telegram_nickname = forms.CharField(max_length=64, required=False, label="Нікнейм в Telegram")
    one_c_ids = forms.CharField(max_length=64, label="ID в 1С")
