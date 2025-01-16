from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count
from django.shortcuts import render
from django.utils import timezone

from logika_statistics.forms import ReportDateBusinessForm
from logika_statistics.models import MasterClassRecord, PaymentRecord, Location
from logika_teachers.models import (
    TutorProfile,
    TeacherFeedback,
    TeacherComment,
    TutorMonthReport,
    RegionalTutorProfile
)
from utils.constants import MONTHS_UA
from utils.get_possible_report_scales import get_possible_report_scales
from utils.get_user_role import get_user_role

scales_new = {
    "Серпень": "2024-08-01_2024-08-25",
    "Вересень": "2023-09-01_2023-09-30",
    "Жовтень": "2023-10-01_2023-10-31",
    "Листопад": "2023-11-01_2023-11-30",
    "Грудень": "2023-12-01_2023-12-20",
    "Січень": "2023-12-21_2024-01-31",
    "Лютий": "2024-02-01_2024-02-29",
    "Березень": "2024-03-01_2024-03-10",
}


def tutor_month_report(request, user_id):
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
        conversion = request.POST.get("conversion")
        if month:
            current_date = timezone.now()
            current_year = current_date.year
            month_number = MONTHS_UA.get(month.strip().lower())
            if month_number > current_date.month:
                current_year -= 1
            # month_reports = TutorMonthReport.objects.filter(
            #     month=month, tutor=tutor, created_at__year=current_year
            # ).all()
            tutor_teachers = tutor.related_teachers.all()
            for teacher in tutor_teachers:
                if not TutorMonthReport.objects.filter(month=month,
                                                       tutor=tutor,
                                                       created_at__year=current_year,
                                                       teacher=teacher).exists():
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
                TutorMonthReport.objects.filter(month=month, tutor=tutor, created_at__year=current_year)
                .order_by("teacher")
                .all()
            )

            if report_id:
                month_report = TutorMonthReport.objects.get(report_id=report_id)
                if is_salary_counted and is_salary_counted[0] == "yes":
                    month_report.is_salary_counted = True

                if conversion:
                    month_report.conversion = conversion

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


@login_required(login_url="/login/")
def get_tutors_conversion(request):
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
        report_start = datetime.strptime(
            report_start.strip(), "%Y-%m-%d"
        ).date()
        report_end = datetime.strptime(report_end.strip(), "%Y-%m-%d").date()
        report_date_default = f"{report_start} - {report_end}"
    else:
        report_start, report_end = scales_new[month_report].split("_")
        report_start = datetime.strptime(
            report_start.strip(), "%Y-%m-%d"
        ).date()
        report_end = datetime.strptime(report_end.strip(), "%Y-%m-%d").date()
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
