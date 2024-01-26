import datetime
import pickle

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views.decorators.cache import never_cache
from transliterate import translit

from logika_administrative.settings import BASE_DIR
from logika_statistics.forms import ReportDateForm, ReportDateBusinessForm
from logika_statistics.models import MasterClassRecord, PaymentRecord, Location
from logika_teachers.forms import (
    TeacherCreateForm,
    TeacherEditProfileForm,
    TeacherFeedbackForm,
)
from logika_teachers.models import (
    TeacherProfile,
    TutorProfile,
    TeacherFeedback,
    TeacherComment,
    TutorMonthReport,
    RegionalTutorProfile,
)
from utils.count_teacher_performance import get_teacher_performance_by_month
from utils.get_teacher_groups import get_teacher_groups
from utils.get_teacher_locations import get_teacher_locations
from utils.get_user_role import get_user_role
from utils.lms_authentication import get_authenticated_session
from utils.logika_scripts import get_conversion

scales_new = {
    "Серпень": "2023-08-01_2023-08-31",
    "Вересень": "2023-09-01_2023-09-30",
    "Жовтень": "2023-10-01_2023-10-31",
    "Листопад": "2023-11-01_2023-11-30",
    "Грудень": "2023-12-01_2023-12-31",
    "Січень": "2024-01-01_2024-01-14",
}


@login_required
def teacher_profile(request, id, tutor_id=None):
    user_role = get_user_role(request.user)
    if user_role == "tutor":
        tutor_profile = TutorProfile.objects.filter(user=request.user).first()
        teacher = TeacherProfile.objects.filter(id=id).first()
    if user_role == "regional_tutor" or user_role == "admin":
        teacher = TeacherProfile.objects.filter(id=id).first()
        tutor_profile = TutorProfile.objects.filter(id=tutor_id).first()

    feedbacks = (
        TeacherFeedback.objects.filter(teacher=teacher, tutor=tutor_profile)
        .order_by("-created_at")
        .all()
    )

    recent_predicted_churns = (
        pickle.loads(feedbacks[0].predicted_churn_object)
        if feedbacks and feedbacks[0].predicted_churn_object
        else None
    )

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
            "tutor_profile": tutor_profile,
        },
    )


@login_required
def edit_teacher_profile(request, id):
    teacher_profile = TeacherProfile.objects.filter(id=id).first()

    if request.method == "POST":
        form = TeacherEditProfileForm(request.POST)
        if form.is_valid():
            teacher_profile.user.first_name = form.cleaned_data["first_name"]
            teacher_profile.user.last_name = form.cleaned_data["last_name"]
            teacher_profile.phone_number = form.cleaned_data["phone_number"]
            teacher_profile.lms_id = form.cleaned_data["lms_id"]
            teacher_profile.telegram_nickname = form.cleaned_data["telegram_nickname"]
            teacher_profile.one_c_ids = form.cleaned_data["one_c_ids"]
            teacher_profile.user.save()
            teacher_profile.save()
            return redirect("logika_teachers:teacher-profile", id=id)
    else:
        initial_data = {
            "teacher_id": id,
            "first_name": teacher_profile.user.first_name,
            "last_name": teacher_profile.user.first_name,
            "phone_number": teacher_profile.phone_number,
            "lms_id": teacher_profile.lms_id,
            "telegram_nickname": teacher_profile.telegram_nickname,
            "one_c_ids": teacher_profile.one_c_ids,
        }
        form = TeacherEditProfileForm(initial=initial_data)

    return render(
        request,
        "logika_teachers/edit_teacher_profile.html",
        {
            "form": form,
            "teacher_id": id,
            "teacher_profile": teacher_profile,
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


@login_required()
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
        teacher_groups = request.POST.getlist("groups")
        if month and locations:
            result, zero_performance_lessons = get_teacher_performance_by_month(
                teacher_id, locations, month_dict[month], teacher_groups
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
                    group_title = group_data["title"].replace("_", " ")
                    groups_data[group] = {}
                    groups_data[group]["average"] = round(
                        sum(result[group]) / len(result[group]) if result[group] else 0,
                        1,
                    )
                    groups_data[group]["max"] = round(
                        max(result[group]) if result[group] else 0, 1
                    )
                    groups_data[group]["min"] = round(
                        min(result[group]) if result[group] else 0, 1
                    )
                    groups_data[group]["title"] = group_title
                    groups_data["teacher_average"] += groups_data[group]["average"]
                groups_data["teacher_average"] = round(
                    groups_data["teacher_average"] / group_count if group_count else 0,
                    1,
                )
            print(zero_performance_lessons)
            return render(
                request,
                "logika_teachers/teacher_performance.html",
                {
                    "groups_data": groups_data,
                    "teachers_locations": get_teacher_locations(teacher_id),
                    "teacher_groups": get_teacher_groups(teacher_id),
                    "teacher": teacher,
                    "zero_performance_lessons": zero_performance_lessons,
                    "form_data": {
                        "month": month,
                        "locations": locations,
                        "chosen_groups": teacher_groups,
                    },
                },
            )
    return render(
        request,
        "logika_teachers/teacher_performance.html",
        {
            "teachers_locations": get_teacher_locations(teacher_id),
            "teacher_groups": get_teacher_groups(teacher_id),
            "teacher": teacher,
        },
    )


def tutor_results(request):
    return render(request, "logika_teachers/tutor_results.html")


def tutor_month_report(request, user_id):
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
    user = User.objects.get(id=user_id)
    tutor = TutorProfile.objects.get(user=user)
    regional_tutor_profile = None
    if request.method == "POST":
        if get_user_role(request.user) != "tutor":
            regional_tutor_profile = RegionalTutorProfile.objects.get(user=request.user)
        month = request.POST.get("month")
        churns_percent = request.POST.get("churns_percent")
        category = request.POST.get("category")
        is_salary_counted = request.POST.getlist("is_salary_counted")
        report_id = request.POST.get("report_id")
        if month:
            month_reports = TutorMonthReport.objects.filter(
                month=month, tutor=tutor
            ).all()
            if not month_reports:
                tutor_teachers = tutor.related_teachers.all()
                for teacher in tutor_teachers:
                    new_month_report = TutorMonthReport(
                        teacher=teacher,
                        churns_percent="-",
                        performance_percent="-",
                        conversion="-",
                        month=month,
                        tutor=tutor,
                    )
                    new_month_report.save()
            month_reports = (
                TutorMonthReport.objects.filter(month=month, tutor=tutor)
                .order_by("teacher")
                .all()
            )
            if report_id:
                month_report = TutorMonthReport.objects.get(report_id=report_id)
                if is_salary_counted and is_salary_counted[0] == "yes":
                    month_report.is_salary_counted = True

                if churns_percent:
                    month_report.churns_percent = churns_percent

                if category:
                    month_report.category = category
                month_report.save()

            return render(
                request,
                "logika_teachers/tutor_month_report.html",
                {
                    "tutor": tutor,
                    "month_reports": month_reports,
                    "regional_tutor_profile": regional_tutor_profile,
                },
            )
    return render(request, "logika_teachers/tutor_month_report.html", {"tutor": tutor})


def add_performance_to_report(request, teacher_id):
    teacher = TeacherProfile.objects.get(id=teacher_id)
    tutor = TutorProfile.objects.get(user=request.user)
    if request.method == "POST":
        print(request.POST)
        month = request.POST.get("month")
        performance = request.POST.get("performance")
        teacher_month_report = TutorMonthReport.objects.filter(
            teacher=teacher, month=month, tutor=tutor
        ).first()
        print(teacher_month_report)
        if teacher_month_report:
            teacher_month_report.performance_percent = performance
            teacher_month_report.save()

        return redirect("logika_teachers:teacher-performance", teacher_id=teacher_id)


def tutor_results_report(request):
    current_user_role = get_user_role(request.user)
    if request.method == "POST":
        regional_tutor_profile = None
        report_start = request.POST.get("report_start")
        report_end = request.POST.get("report_end")
        if current_user_role == "regional_tutor" or current_user_role == "admin":
            regional_tutor_profile = RegionalTutorProfile.objects.get(user=request.user)
            tutors = regional_tutor_profile.related_tutors.all()
        elif current_user_role == "tutor":
            tutor_profile = TutorProfile.objects.get(user=request.user)
            tutors = [tutor_profile]
        data = {}
        for tutor in tutors:
            data[tutor] = {}
            call_summ = 0
            lesson_summ = 0
            for teacher in tutor.related_teachers.order_by("user__first_name").all():
                comments_call = TeacherComment.objects.filter(
                    teacher=teacher,
                    tutor=tutor,
                    created_at__gte=report_start,
                    created_at__lte=report_end,
                    comment_type="call",
                ).all()
                comments_lesson = TeacherComment.objects.filter(
                    teacher=teacher,
                    tutor=tutor,
                    created_at__gte=report_start,
                    created_at__lte=report_end,
                    comment_type="lesson",
                ).all()
                feedbacks = TeacherFeedback.objects.filter(
                    teacher=teacher,
                    tutor=tutor,
                    created_at__gte=report_start,
                    created_at__lte=report_end,
                ).all()
                data[tutor][teacher] = {
                    "call": comments_call,
                    "lesson": comments_lesson,
                    "call_amount": len(comments_call),
                    "lesson_amount": len(comments_lesson),
                    "feedbacks_amount": len(feedbacks),
                    "id": teacher.id,
                }
                call_summ += len(comments_call)
                lesson_summ += len(comments_lesson)
            data[tutor]["total"] = {
                "total_calls": call_summ,
                "total_lessons": lesson_summ,
                "total_teachers": len(data[tutor]),
            }

        return render(
            request,
            "logika_teachers/weekly_tutors_result.html",
            context={
                "data": data,
                "report_start": report_start,
                "report_end": report_end,
                "regional_tutor_profile": regional_tutor_profile,
                "tutors": tutors,
            },
        )
    return render(request, "logika_teachers/weekly_tutors_result.html")


@login_required
def unsub_teacher(request, teacher_id):
    current_user = request.user
    user_role = get_user_role(current_user)
    if not user_role == "tutor":
        return render(request, "error_403.html")

    tutor_profile = TutorProfile.objects.get(user=current_user)
    teacher_profile = TeacherProfile.objects.get(id=teacher_id)
    teacher_profile.related_tutors.remove(tutor_profile)

    return redirect("logika_general:index")


def get_possible_report_scales():
    with open(
        f"{BASE_DIR}/report_scales.txt", "r", encoding="UTF-8"
    ) as report_scales_fileobj:
        scales = report_scales_fileobj.readlines()
    scales_dict = {}
    for i in range(len(scales)):
        scales[i] = scales[i].replace("\n", "").replace("_", " - ")
        month = scales[i].split(":")[0]
        try:
            dates = scales[i].split(":")[1]
        except:
            dates = None
        if month not in scales_dict:
            scales_dict[month] = [dates]
        else:
            scales_dict[month].append(dates)
    possible_report_scales = []
    for key, value in scales_dict.items():
        possible_report_scales.append(key)
        for val in value:
            if val is not None:
                possible_report_scales.append(val)
    return possible_report_scales


@login_required
def get_teacher_conversion(request, teacher_id, tutor_id=None):
    current_user = request.user
    user_role = get_user_role(current_user)
    if not (
        user_role == "tutor" or user_role == "admin" or user_role == "regional_tutor"
    ):
        return render(request, "error_403.html")
    if user_role == "tutor":
        tutor_profile = TutorProfile.objects.get(user=current_user)
    else:
        tutor_profile = TutorProfile.objects.get(id=tutor_id)
    teacher_profile = TeacherProfile.objects.get(id=teacher_id)
    teacher_lms_id = teacher_profile.lms_id

    teacher_locations = list(
        set(
            MasterClassRecord.objects.filter(teacher_lms_id=teacher_lms_id).values_list(
                "location", flat=True
            )
        )
    )
    possible_report_scales = get_possible_report_scales()
    if request.method == "POST":
        month_report = None
        form = ReportDateForm(request.POST)
        if form.is_valid():
            try:
                report_start, report_end = form.cleaned_data["report_scale"].split(
                    " - "
                )
            except ValueError:
                month_report = form.cleaned_data["report_scale"]
        else:
            report_start, report_end = possible_report_scales[-1].split(" - ")

        if not month_report:
            report_start = datetime.datetime.strptime(report_start, "%Y-%m-%d").date()
            report_end = datetime.datetime.strptime(report_end, "%Y-%m-%d").date()
        else:
            report_start, report_end = scales_new[month_report].split("_")
            report_start = datetime.datetime.strptime(report_start, "%Y-%m-%d").date()
            report_end = datetime.datetime.strptime(report_end, "%Y-%m-%d").date()

        teacher_mc_students_queryset = MasterClassRecord.objects.filter(
            start_date__gte=report_start,
            end_date__lte=report_end,
            teacher_lms_id=teacher_lms_id,
        )

        teacher_payments_queryset = PaymentRecord.objects.filter(
            start_date__gte=report_start,
            end_date__lte=report_end,
            teacher_lms_id=teacher_lms_id,
        )

        locations = request.POST.getlist("locations")
        business = request.POST.get("business")

        if locations:
            selected_mc_students_queryset = teacher_mc_students_queryset.filter(
                location__in=locations, business=business
            )

            selected_payments_queryset = teacher_payments_queryset.filter(
                location__in=locations, business=business
            )

            payments_by_location = selected_payments_queryset.values(
                "location"
            ).annotate(payment_count=Count("location"))

            enrolled_by_location = selected_mc_students_queryset.values(
                "location"
            ).annotate(student_count=Count("location"))

            attended_by_location = (
                selected_mc_students_queryset.filter(attended=True)
                .values("location")
                .annotate(student_count=Count("location"))
            )
            conversion_by_location = []
            for location in attended_by_location:
                location_name = location["location"]
                attended_students = location["student_count"]
                payments_amount = 0
                for payment in payments_by_location:
                    if payment["location"] == location_name:
                        payments_amount = payment["payment_count"]
                conversion_by_location.append(
                    {
                        "location": location_name,
                        "conversion": get_conversion(
                            payments_amount, attended_students
                        ),
                    }
                )
            total_enrolled = sum(
                student["student_count"] for student in enrolled_by_location
            )
            total_payments = sum(
                payment["payment_count"] for payment in payments_by_location
            )
            total_attended = sum(
                student["student_count"] for student in attended_by_location
            )
            total_conversion = get_conversion(total_payments, total_attended)

            return render(
                request,
                "logika_teachers/teacher_conversion.html",
                {
                    "teachers_locations": teacher_locations,
                    "teacher": teacher_profile,
                    "enrolled_by_location": enrolled_by_location,
                    "attended_by_location": attended_by_location,
                    "payments_by_location": payments_by_location,
                    "conversion_by_location": conversion_by_location,
                    "total_enrolled": total_enrolled,
                    "total_payments": total_payments,
                    "total_attended": total_attended,
                    "total_conversion": total_conversion,
                    "report_scales": possible_report_scales,
                    "tutor_profile": tutor_profile,
                    "form_data": {
                        "locations": locations,
                        "report_scale": form.cleaned_data["report_scale"],
                    },
                },
            )
    return render(
        request,
        "logika_teachers/teacher_conversion.html",
        {
            "teachers_locations": teacher_locations,
            "teacher": teacher_profile,
            "report_scales": possible_report_scales,
            "tutor_profile": tutor_profile,
        },
    )


@login_required(login_url="/login/")
def get_tutors_conversion(request):
    #
    # possible_report_scales = get_possible_report_scales()
    business = "programming"
    month_report = None
    possible_report_scales = get_possible_report_scales()
    if request.method == "POST":
        form = ReportDateBusinessForm(request.POST)
        if form.is_valid():
            try:
                report_start, report_end = form.cleaned_data["report_scale"].split(
                    " - "
                )
            except ValueError:
                month_report = form.cleaned_data["report_scale"]

            business = form.cleaned_data["report_business"]
        else:
            report_start, report_end = possible_report_scales[-1].split(" - ")
    else:
        report_start, report_end = possible_report_scales[-1].split(" - ")
    if not month_report:
        report_start = datetime.datetime.strptime(
            report_start.strip(), "%Y-%m-%d"
        ).date()
        report_end = datetime.datetime.strptime(report_end.strip(), "%Y-%m-%d").date()
        report_date_default = f"{report_start} - {report_end}"
    else:
        report_start, report_end = scales_new[month_report].split("_")
        report_start = datetime.datetime.strptime(
            report_start.strip(), "%Y-%m-%d"
        ).date()
        report_end = datetime.datetime.strptime(report_end.strip(), "%Y-%m-%d").date()
        report_date_default = f"{report_start} - {report_end}"

    current_user = request.user
    user_role = get_user_role(current_user)
    if not (
        user_role == "tutor"
        or user_role == "admin"
        or user_role == "regional_tutor"
        or user_role == "regional_manager"
        or user_role == "territorial_manager"
    ):
        return render(request, "error_403.html")

    tutor_profiles = []

    if user_role == "tutor":
        tutor_profiles = [
            TutorProfile.objects.get(user=current_user),
        ]

    elif user_role == "regional_tutor":
        regional_tutor_profile = RegionalTutorProfile.objects.get(user=current_user)
        tutor_profiles = regional_tutor_profile.related_tutors.all()

    elif user_role == "regional_manager" or user_role == "territorial_manager":
        if user_role == "regional_manager":
            regional_manager_name = (
                f"{current_user.last_name} {current_user.first_name}"
            )
            locations = list(
                set(
                    Location.objects.filter(
                        regional_manager=regional_manager_name
                    ).values_list("lms_location_name", flat=True)
                )
            )
        else:
            territorial_manager_name = (
                f"{current_user.last_name} {current_user.first_name}"
            )
            locations = list(
                set(
                    Location.objects.filter(
                        territorial_manager=territorial_manager_name
                    ).values_list("lms_location_name", flat=True)
                )
            )
        teachers = list(
            set(
                MasterClassRecord.objects.filter(
                    location__in=locations,
                    start_date__gte=report_start,
                    end_date__lte=report_end,
                    business=business,
                ).values_list("teacher_lms_id", flat=True)
            )
        )
        tutor_profiles = []
        for teacher in teachers:
            tutor_profile = TutorProfile.objects.filter(
                related_teachers__lms_id=teacher
            ).all()
            for profile in tutor_profile:
                tutor_profiles.append(profile)

    elif user_role == "admin":
        tutor_profiles = TutorProfile.objects.all()

    teachers_by_tutors_data = {}
    for tutor in tutor_profiles:
        teachers = tutor.related_teachers.all()
        for teacher in teachers:
            teacher_locations = list(
                set(
                    MasterClassRecord.objects.filter(
                        teacher_lms_id=teacher.lms_id
                    ).values_list("location", flat=True)
                )
            )
            teacher_mc_students_queryset = MasterClassRecord.objects.filter(
                start_date__gte=report_start,
                end_date__lte=report_end,
                teacher_lms_id=teacher.lms_id,
                location__in=teacher_locations,
                business=business,
            )

            teacher_payments_queryset = PaymentRecord.objects.filter(
                start_date__gte=report_start,
                end_date__lte=report_end,
                teacher_lms_id=teacher.lms_id,
                location__in=teacher_locations,
                business=business,
            )

            payments_by_location = teacher_payments_queryset.values(
                "location"
            ).annotate(payment_count=Count("location"))

            enrolled_by_location = teacher_mc_students_queryset.values(
                "location"
            ).annotate(student_count=Count("location"))

            attended_by_location = (
                teacher_mc_students_queryset.filter(attended=True)
                .values("location")
                .annotate(student_count=Count("location"))
            )
            if len(attended_by_location) != 0:
                tutor_name = tutor.user.get_full_name()
                teacher_name = teacher.user.get_full_name()

                if tutor_name not in teachers_by_tutors_data:
                    teachers_by_tutors_data[tutor_name] = {
                        "teachers": {},
                        "tutor_profile": tutor,
                    }

                if teacher_name not in teachers_by_tutors_data[tutor_name]:
                    teachers_by_tutors_data[tutor_name]["teachers"][teacher_name] = {
                        "enrolled_by_locations": enrolled_by_location,
                        "attended_by_locations": attended_by_location,
                        "payments_by_locations": payments_by_location,
                        "teacher_profile": teacher,
                    }

    context = {
        "teachers_tutors_data": teachers_by_tutors_data,
        "report_date_default": report_date_default,
        "report_scales": possible_report_scales,
    }
    return render(
        request,
        template_name="logika_teachers/tutor_teachers_statistics.html",
        context=context,
    )
