from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from logika_teachers.forms import (
    TeacherCreateForm,
    TeacherFeedbackForm,
    TeacherCommentForm,
    TeacherPerformanceForm,
)
from logika_teachers.models import (
    TeacherProfile,
    TutorProfile,
    TeacherFeedback,
    TeacherComment,
)
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
import pickle
from django.views.decorators.cache import cache_page, never_cache
from transliterate import translit
from utils.get_user_role import get_user_role
from utils.lms_authentication import get_authenticated_session
from utils.count_teacher_performance import get_teacher_performance_by_month
from utils.get_teacher_locations import get_teacher_locations


@login_required
def teacher_profile(request, id):
    user_role = get_user_role(request.user)
    if user_role == "tutor":
        tutor = TutorProfile.objects.filter(user=request.user).first()
        teacher = TeacherProfile.objects.filter(id=id).first()
        feedbacks = (
            TeacherFeedback.objects.filter(teacher=teacher, tutor=tutor)
            .order_by("-created_at")
            .all()
        )

        recent_predicted_churns = (
            pickle.loads(feedbacks[0].predicted_churn_object)
            if feedbacks and feedbacks[0].predicted_churn_object
            else None
        )

    tutor_profile = TutorProfile.objects.filter(user=request.user).first()
    call_comments = (
        TeacherComment.objects.filter(
            teacher=teacher, tutor=tutor_profile, comment_type="call"
        )
        .order_by("-created_at")
        .all()
    )
    lesson_comments = (
        TeacherComment.objects.filter(
            teacher=teacher, tutor=tutor_profile, comment_type="lesson"
        )
        .order_by("-created_at")
        .all()
    )
    all_comments = (
        TeacherComment.objects.filter(teacher=teacher, tutor=tutor_profile)
        .order_by("-created_at")
        .all()
    )

    teacher_profile = TeacherProfile.objects.filter(id=id).first()
    return render(
        request,
        "logika_teachers/teacher_profile.html",
        {
            "teacher_profile": teacher_profile,
            "user_role": user_role,
            "feedbacks": feedbacks,
            "call_comments": call_comments,
            "lesson_comments": lesson_comments,
            "all_comments": all_comments,
            "recent_feedback_churn": recent_predicted_churns,
        },
    )


@login_required
def create_teacher(request):
    alerts = []
    if request.method == "POST":
        form = TeacherCreateForm(request.POST)
        if form.is_valid():
            form_data = form.cleaned_data
            full_name = f"{form_data['first_name']} {form_data['last_name']}"
            username = (
                translit(full_name, "ru", reversed=True)
                .lower()
                .replace(" ", "_")
                .replace("'", "")
                .replace("і", "i")
                .replace("є", "ye")
                .replace("ї", "yi")
                .replace("ґ", "g")
            )
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
                alerts.append(
                    {
                        "title": "Неможливо створити викладача",
                        "content": "Створювати викладача може лише тьютор. Якщо ви тьютор - зверніться до вашого РТ.",
                    }
                )

                return render(
                    request,
                    "logika_teachers/create_teacher.html",
                    {"form": form, "alerts": alerts},
                )
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
            return render(
                request,
                "logika_teachers/login_password_responce.html",
                {"username": username, "password": password, "created": created_user},
            )
        else:
            alerts.append(
                {
                    "title": "Неможливо створити викладача",
                    "content": f"Перевірте правильність введених даних. {form.errors}",
                }
            )
            return render(
                request,
                "logika_teachers/create_teacher.html",
                {"form": form, "alerts": alerts},
            )

    else:
        form = TeacherCreateForm()

    return render(request, "logika_teachers/create_teacher.html", {"form": form})


@login_required
def teacher_feedback_form(request, teacher_id, tutor_id):
    teacher_user = User.objects.filter(id=teacher_id).first()
    teacher_profile = TeacherProfile.objects.filter(user=teacher_user).first()
    form_data = None
    tutor_user = User.objects.filter(id=tutor_id).first()
    tutor_profile = TutorProfile.objects.filter(user=tutor_user).first()
    tutor_name = tutor_user.get_full_name()
    alerts = []
    if request.method == "POST":
        form = TeacherFeedbackForm(request.POST)
        if form.is_valid():
            form_data = form.cleaned_data
            predicted_churn_ids = request.POST.getlist("predicted_churn_id[]")
            predicted_churn_descriptions = request.POST.getlist(
                "predicted_churn_description[]"
            )
            for student_id in predicted_churn_ids:
                if student_id != "":
                    student_url = f"https://lms.logikaschool.com/api/v1/student/view/{student_id}?expand=branch,group"
                    session = get_authenticated_session()
                    response = session.get(student_url)
                    if response.status_code == 404:
                        alerts.append(
                            {
                                "title": "Невірна форма",
                                "content": f"Невірно вказано ID учня {student_id}. Такого учня не існує.",
                            }
                        )
            if len(alerts) > 0:
                return render(
                    request,
                    "logika_teachers/feedback_form.html",
                    {
                        "teacher_profile": teacher_profile,
                        "teacher_id": teacher_id,
                        "tutor_id": tutor_id,
                        "form": form,
                        "alerts": alerts,
                        "tutor_name": tutor_name,
                        "form_data": form_data,
                    },
                )

            new_form = TeacherFeedback(
                teacher=teacher_profile,
                tutor=tutor_profile,
                mistakes=form_data["mistakes"],
                lesson_mark=form_data["lesson_mark"],
                additional_problems=form_data["additional_problems"],
                problems=form_data["problems"],
                technical_problems=form_data["technical_problems"],
                km_work_comment=form_data["km_work_comment"],
                tutor_work_comment=form_data["tutor_work_comment"],
                km_work_mark=form_data["km_work_mark"],
                tutor_work_mark=form_data["tutor_work_mark"],
            )
            churns = {}
            for i in range(len(predicted_churn_ids)):
                churns[predicted_churn_ids[i]] = predicted_churn_descriptions[i]

            new_form.predicted_churn_object = pickle.dumps(churns)
            new_form.save()
            return redirect("/")
        else:
            alerts.append(
                {
                    "title": "Невірна форма",
                    "content": f"Ви заповнили не всі поля, або додали додаткові проблеми в полі 'Проблеми'.",
                }
            )
    else:
        form = TeacherFeedbackForm()

    return render(
        request,
        "logika_teachers/feedback_form.html",
        {
            "teacher_profile": teacher_profile,
            "teacher_id": teacher_id,
            "tutor_id": tutor_id,
            "form": form,
            "alerts": alerts,
            "tutor_name": tutor_name,
            "form_data": form_data,
        },
    )


@login_required
@never_cache
# @cache_page(60*60*24)
def view_forms(request, feedback_id):
    feedback = TeacherFeedback.objects.filter(id=feedback_id).first()
    user_role = get_user_role(request.user)
    predicted_churns = (
        pickle.loads(feedback.predicted_churn_object)
        if feedback.predicted_churn_object
        else None
    )
    churns_data = []
    session = get_authenticated_session()
    if predicted_churns:
        for predicted_churn in predicted_churns:
            student_url = f"https://lms.logikaschool.com/api/v1/student/view/{predicted_churn}?expand=branch,group"
            student_response = session.get(student_url)
            if student_response.status_code == 200:
                student_info = {}
                student_info["student_id"] = predicted_churn
                student_data = student_response.json()["data"]
                student_info[
                    "student_name"
                ] = f"{student_data['first_name']} {student_data['last_name']}"
                group_data = student_data["group"]
                if group_data:
                    student_info[
                        "group_link"
                    ] = f'<a href="https://lms.logikaschool.com/group/view/{group_data["id"]}" target="_blank">{group_data["title"]}</a>'
                churns_data.append(student_info)
    return render(
        request,
        "logika_teachers/view_forms.html",
        {
            "feedback": feedback,
            "user_role": user_role,
            "predicted_churns": predicted_churns,
            "churns_data": churns_data,
        },
    )


@login_required
def create_comment(request):
    request_data = request.POST
    comment_type = request_data.get("comment_type")
    teacher_profile = TeacherProfile.objects.filter(
        id=request_data.get("teacher")
    ).first()
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
        feedback = TeacherFeedback.objects.filter(
            id=request_data.get("feedback_id")
        ).first()
        comment = TeacherComment(
            comment=request_data.get("comment"),
            comment_type=comment_type,
            feedback=feedback,
            teacher=teacher_profile,
            tutor=tutor_profile,
        )
        comment.save()

    if comment_type == "predicted_churn":
        feedback = TeacherFeedback.objects.filter(
            id=request_data.get("feedback_id")
        ).first()
        comment = TeacherComment(
            comment=request_data.get("comment"),
            comment_type=comment_type,
            feedback=feedback,
            teacher=teacher_profile,
            tutor=tutor_profile,
            churn_id=request_data.get("churn"),
        )
        comment.save()
    next = request.POST.get("next", "/")
    return HttpResponseRedirect(next)


@login_required
def refresh_credentials(request, user_id):
    user = User.objects.filter(id=user_id).first()
    if user:
        full_name = user.get_full_name()
        username = (
            translit(full_name, "ru", reversed=True)
            .lower()
            .replace(" ", "_")
            .replace("'", "")
            .replace("і", "i")
            .replace("є", "ye")
            .replace("ї", "yi")
            .replace("ґ", "g")
        )
        password = User.objects.make_random_password(length=8)
        user.username = username
        user.set_password(password)
        user.save()
        return render(
            request,
            "logika_teachers/login_password_responce.html",
            {"username": username, "password": password, "created": True},
        )


def teacher_performance(request, teacher_id):
    teacher = TeacherProfile.objects.filter(id=teacher_id).first()
    if request.method == "POST":
        month_dict = {
            "Січень": 1,
            "Лютий": 2,
            "Березень": 3,
            "Квітень": 4,
            "Травень": 5,
            "Червень": 6,
            "Липень": 7,
            "Серпень": 8,
            "Вересень": 9,
            "Жовтень": 10,
            "Листопад": 11,
            "Грудень": 12,
        }
        locations = request.POST.getlist("locations")
        month = request.POST.get("month")
        if month and locations:
            result = get_teacher_performance_by_month(
                teacher_id, locations, month_dict[month]
            )
            groups_data = {}

            if result:
                session = get_authenticated_session()
                groups_data["teacher_average"] = 0
                group_count = 0
                for group in result:
                    if len(result[group]) < 1:
                        continue
                    group_count += 1
                    group_resp = session.get(
                        f"https://lms.logikaschool.com/api/v1/group/{group}"
                    )
                    group_data = group_resp.json()["data"]
                    group_title = group_data["title"].replace("_", "")
                    groups_data[group] = {}
                    groups_data[group]["average"] = (
                        sum(result[group]) / len(result[group]) if result[group] else 0
                    )
                    groups_data[group]["max"] = (
                        max(result[group]) if result[group] else 0
                    )
                    groups_data[group]["min"] = (
                        min(result[group]) if result[group] else 0
                    )
                    groups_data[group]["title"] = group_title
                    groups_data["teacher_average"] += groups_data[group]["average"]
                groups_data["teacher_average"] = (
                    groups_data["teacher_average"] / group_count if group_count else 0
                )
            return render(
                request,
                "logika_teachers/teacher_performance.html",
                {
                    "groups_data": groups_data,
                    "teachers_locations": get_teacher_locations(teacher_id),
                    "teacher": teacher,
                    "form_data": {"month": month, "locations": locations},
                },
            )
    return render(
        request,
        "logika_teachers/teacher_performance.html",
        {
            "teachers_locations": get_teacher_locations(teacher_id),
            "teacher": teacher,
        },
    )


def tutor_results(request):
    return render(request, "logika_teachers/tutor_results.html")
