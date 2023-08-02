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

