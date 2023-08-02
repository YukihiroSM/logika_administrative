from django.shortcuts import render, redirect
from logika_teachers.forms import TeacherCreateForm
from logika_teachers.models import TeacherProfile, TutorProfile
from django.contrib.auth.models import User
from transliterate import translit
from utils.get_user_role import get_user_role


def teacher_profile(request, id):
    user_role = get_user_role(request.user)
    teacher_profile = TeacherProfile.objects.filter(id=id).first()
    return render(request, "logika_teachers/teacher_profile.html",
                  {"teacher_profile": teacher_profile, "auser_role": user_role})


def create_teacher(request):
    alerts = []
    if request.method == "POST":
        form = TeacherCreateForm(request.POST)
        if form.is_valid():
            form_data = form.cleaned_data
            full_name = f"{form_data['first_name']} {form_data['last_name']}"
            username = translit(full_name, "ru", reversed=True).lower().replace(" ", "_").replace("'", "")
            password = User.objects.make_random_password(length=8)
            teacher_user, created_user = User.objects.get_or_create(
                username=username,
            )
            if created_user:
                teacher_user.first_name = form_data["first_name"]
                teacher_user.last_name = form_data["last_name"]
                teacher_user.email = form_data["email"]
                teacher_user.set_password(password)
                teacher_user.save()

            tutor_profile = TutorProfile.objects.filter(user=request.user).first()
            if not tutor_profile:
                alerts.append({
                    "title": "Неможливо створити викладача",
                    "content": "Створювати викладача може лише тьютор. Якщо ви тьютор - зверніться до вашого РТ."
                })

                return render(request, "logika_teachers/create_teacher.html", {"form": form, "alerts": alerts})
            if created_user:
                teacher_profile = TeacherProfile(
                    user=teacher_user,
                    lms_id=form_data["lms_id"],
                    telegram_nickname=form_data["telegram_nickname"],
                    phone_number=form_data["phone_number"],
                )

                teacher_profile.save()
            else:
                teacher_profile = TeacherProfile.objects.get(user=teacher_user)
            teacher_profile.related_tutors.add(tutor_profile)
            teacher_profile.save()
            return render(request, "logika_teachers/login_password_responce.html",
                          {"username": username, "password": password, "created": created_user})

    else:
        form = TeacherCreateForm()

    return render(request, "logika_teachers/create_teacher.html", {"form": form})