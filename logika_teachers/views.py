from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from logika_teachers.forms import TeacherCreateForm, TeacherFeedbackForm, TeacherCommentForm
from logika_teachers.models import (
    TeacherProfile,
    TutorProfile,
    TeacherFeedback,
    TeacherComment
)
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from transliterate import translit
from utils.get_user_role import get_user_role


@login_required
def teacher_profile(request, id):
    user_role = get_user_role(request.user)
    if user_role == "tutor":
        teacher = TeacherProfile.objects.filter(id=id).first()
        feedbacks = TeacherFeedback.objects.filter(teacher=teacher).order_by("-created_at").all()

    tutor_profile = TutorProfile.objects.filter(user=request.user).first()
    call_comments = TeacherComment.objects.filter(teacher=teacher, tutor=tutor_profile, comment_type="call").order_by("-created_at").all()
    lesson_comments = TeacherComment.objects.filter(teacher=teacher, tutor=tutor_profile, comment_type="lesson").order_by("-created_at").all()
    all_comments = TeacherComment.objects.filter(teacher=teacher, tutor=tutor_profile).order_by("-created_at").all()

    teacher_profile = TeacherProfile.objects.filter(id=id).first()
    return render(request, "logika_teachers/teacher_profile.html",
                  {"teacher_profile": teacher_profile, "user_role": user_role, "feedbacks": feedbacks,
                   "call_comments": call_comments, "lesson_comments": lesson_comments, "all_comments": all_comments})


@login_required
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
            alerts.append({
                "title": "Неможливо створити викладача",
                "content": f"Перевірте правильність введених даних. {form.errors}"
            })
            return render(request, "logika_teachers/create_teacher.html", {"form": form, "alerts": alerts})

    else:
        form = TeacherCreateForm()

    return render(request, "logika_teachers/create_teacher.html", {"form": form})


def teacher_feedback_form(request, teacher_id, tutor_id):
    teacher_user = User.objects.filter(id=teacher_id).first()
    teacher_profile = TeacherProfile.objects.filter(user=teacher_user).first()

    tutor_user = User.objects.filter(id=tutor_id).first()
    tutor_profile = TutorProfile.objects.filter(user=tutor_user).first()
    alerts = []
    if request.method == "POST":
        form = TeacherFeedbackForm(request.POST)
        if form.is_valid():
            form_data = form.cleaned_data
            new_form = TeacherFeedback(
                teacher=teacher_profile,
                tutor=tutor_profile,
                mistakes=form_data["mistakes"],
                lesson_mark=form_data["lesson_mark"],
                additional_problems=form_data["additional_problems"],
                problems=form_data["problems"],
                predicted_churn=form_data["predicted_churn"],
                technical_problems=form_data["technical_problems"],
                km_work_comment=form_data["km_work_comment"],
                tutor_work_comment=form_data["tutor_work_comment"],
            )
            new_form.save()
            return redirect("/")
        else:
            alerts.append({
                "title": "Невірна форма",
                "content": f"Ви заповнили не всі поля, або додали додаткові проблеми в полі 'Проблеми'.",
            })
    else:
        form = TeacherFeedbackForm()

    return render(request, "logika_teachers/feedback_form.html",
                  {"teacher_profile": teacher_profile,
                   "teacher_id": teacher_id, "tutor_id": tutor_id,
                   "form": form, "alerts": alerts})


def view_forms(request, feedback_id):
    feedback = TeacherFeedback.objects.filter(id=feedback_id).first()
    user_role = get_user_role(request.user)
    return render(request, "logika_teachers/view_forms.html", {"feedback": feedback, "user_role": user_role})


def create_comment(request):
    request_data = request.GET
    comment_type = request_data.get("comment_type")
    teacher_profile = TeacherProfile.objects.filter(id=request_data.get("teacher")).first()
    tutor_profile = TutorProfile.objects.filter(user=request.user).first()
    if comment_type == "other" or comment_type == "call":
        comment = TeacherComment(
            comment=request_data.get("comment"),
            comment_type=comment_type,
            teacher=teacher_profile,
            tutor=tutor_profile,
        )
        comment.save()
    if comment_type == "lesson":
        comment = TeacherComment(
            comment=request_data.get("comment"),
            comment_type=comment_type,
            group_id=request_data.get("group_id"),
            teacher=teacher_profile,
            tutor=tutor_profile,
        )
        comment.save()

    if comment_type == "feedback":
        feedback = TeacherFeedback.objects.filter(id=request_data.get("feedback_id")).first()
        comment = TeacherComment(
            comment=request_data.get("comment"),
            comment_type=comment_type,
            feedback=feedback,
            teacher=teacher_profile,
            tutor=tutor_profile,
        )
        comment.save()
    next = request.GET.get('next', '/')
    return HttpResponseRedirect(next)