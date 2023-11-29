import csv
import datetime
import os

from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.template import loader
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from logika_administrative.settings import BASE_DIR
from logika_general.models import (
    ClientManagerProfile,
    RegionalManagerProfile,
    TerritorialManagerProfile,
)
from logika_teachers.models import TutorProfile
from utils.get_user_role import get_user_role
from utils.lms_authentication import get_authenticated_session
from .forms import ReportDateForm, UpdateLocationForm
from .models import (
    Location,
    StudentReport,
    ClientManagerReport,
    LocationReport,
    CourseReport,
)
from .utils import (
    retrieve_group_ids_from_csv,
    get_lessons_links_extended,
)


def is_member(user, group_name):
    return user.groups.filter(name=group_name).exists()


def results(request):
    report_scale = request.POST.get("report_scale", None)
    print(report_scale)


def health(request):
    return {"status": "OK"}


base_path = os.path.dirname(os.path.dirname(__file__))

scales_new = {
    "Серпень": "2023-08-01_2023-08-31",
    "Вересень": "2023-09-01_2023-09-30",
    "Жовтень": "2023-10-01_2023-10-31",
    "Листопад": "2023-11-01_2023-11-26",
}


@csrf_exempt
def collect_lessons_links_extended(request):
    request_data_GET = dict(request.GET)
    report_start = request_data_GET.get("report_start", [""])[0]
    report_end = request_data_GET.get("report_end", [""])[0]
    auth = get_authenticated_session()
    ids = retrieve_group_ids_from_csv(
        auth, report_start=report_start, report_end=report_end
    )
    result_data = get_lessons_links_extended(ids=ids)
    response = HttpResponse(
        content_type="text/csv",
        headers={
            "Content-Disposition": 'attachment; filename="lessons_schedule_links.csv"'
        },
    )
    response.write("\ufeff".encode("utf8"))

    writer = csv.writer(response)
    writer.writerow(
        [
            "ID Групи",
            "Назва групи",
            "Посилання",
            "Викладач",
            "КМ",
            "Назва курсу",
            "Дата, час наступного уроку",
        ]
    )
    for group in result_data:
        writer.writerow(
            [
                group.get("group"),
                group.get("group_name"),
                group.get("link"),
                group.get("teacher_name"),
                group.get("curator_name"),
                group.get("course_name"),
                group.get("next_lesson_time"),
            ]
        )
    response["Content-Encoding"] = "utf-8"
    return response


def get_possible_report_scales():
    month_report = None
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


def get_locations_by_regional(regional_name):
    locations = Location.objects.filter(regional_manager=regional_name).values_list(
        "lms_location_name", flat=True
    )
    return locations


def get_locations_by_territorial(territorial_name):
    locations = Location.objects.filter(
        territorial_manager=territorial_name
    ).values_list("lms_location_name", flat=True)
    return locations


@login_required(login_url="/login/")
def programming_report_updated(request):
    month_report = None
    possible_report_scales = get_possible_report_scales()
    if request.method == "POST":
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
    else:
        report_start, report_end = possible_report_scales[-1].split(" - ")
    if not month_report:
        report_start = datetime.datetime.strptime(report_start, "%Y-%m-%d").date()
        report_end = datetime.datetime.strptime(report_end, "%Y-%m-%d").date()
        report_date_default = f"{report_start} - {report_end}"
    else:
        report_start, report_end = scales_new[month_report].split("_")
        report_start = datetime.datetime.strptime(report_start, "%Y-%m-%d").date()
        report_end = datetime.datetime.strptime(report_end, "%Y-%m-%d").date()
        report_date_default = f"{report_start} - {report_end}"

    user_role = get_user_role(request.user)
    if user_role == "admin":
        location_reports = (
            LocationReport.objects.filter(start_date=report_start, end_date=report_end)
            .exclude(territorial_manager="UNKNOWN", regional_manager__isnull=True)
            .all()
        )
        client_manager_reports = (
            ClientManagerReport.objects.filter(
                start_date=report_start, end_date=report_end
            )
            .exclude(territorial_manager="UNKNOWN", regional_manager__isnull=True)
            .all()
        )
        territorial_managers = (
            StudentReport.objects.filter(
                start_date__gte=report_start, end_date__lte=report_end
            )
            .exclude(
                territorial_manager__isnull=True,
                territorial_manager="UNKNOWN",
                regional_manager__isnull=True,
            )
            .values_list("territorial_manager", flat=True)
            .distinct()
        )
        course_report = (
            CourseReport.objects.filter(start_date=report_start, end_date=report_end)
            .exclude(territorial_manager="UNKNOWN", regional_manager__isnull=True)
            .all()
        )

    if user_role == "client_manager":
        client_manager_profile = ClientManagerProfile.objects.filter(
            user=request.user
        ).first()
        client_manager_name = f"{request.user.last_name} {request.user.first_name}"
        related_tms = client_manager_profile.related_tms.all()
        territorial_managers = [
            f"{tm.user.last_name} {tm.user.first_name}" for tm in related_tms
        ]
        client_manager_locations = (
            Location.objects.filter(client_manager=client_manager_name)
            .all()
            .values_list("lms_location_name", flat=True)
        )

        location_reports = (
            LocationReport.objects.filter(
                start_date=report_start,
                end_date=report_end,
                location_name__in=client_manager_locations,
            )
            .exclude(territorial_manager="UNKNOWN", regional_manager__isnull=True)
            .all()
        )
        client_manager_reports = (
            ClientManagerReport.objects.filter(
                start_date=report_start,
                end_date=report_end,
                client_manager=client_manager_name,
            )
            .exclude(territorial_manager="UNKNOWN", regional_manager__isnull=True)
            .all()
        )
    if user_role == "territorial_manager":
        territorial_managers = [f"{request.user.last_name} {request.user.first_name}"]
        location_reports = (
            LocationReport.objects.filter(
                start_date=report_start,
                end_date=report_end,
                territorial_manager__in=territorial_managers,
            )
            .exclude(territorial_manager="UNKNOWN", regional_manager__isnull=True)
            .all()
        )
        client_manager_reports = (
            ClientManagerReport.objects.filter(
                start_date=report_start,
                end_date=report_end,
                territorial_manager__in=territorial_managers,
            )
            .exclude(territorial_manager="UNKNOWN", regional_manager__isnull=True)
            .all()
        )
    if user_role == "regional_manager":
        regional_manager_profile = RegionalManagerProfile.objects.get(user=request.user)
        territorial_managers_objects = (
            regional_manager_profile.territorial_managers.all()
        )
        territorial_managers = [
            f"{tm.user.last_name} {tm.user.first_name}"
            for tm in territorial_managers_objects
        ]

        location_reports = (
            LocationReport.objects.filter(
                start_date=report_start,
                end_date=report_end,
                territorial_manager__in=territorial_managers,
                regional_manager=f"{request.user.last_name} {request.user.first_name}",
            )
            .exclude(territorial_manager="UNKNOWN", regional_manager__isnull=True)
            .all()
        )
        client_manager_reports = (
            ClientManagerReport.objects.filter(
                start_date=report_start,
                end_date=report_end,
                territorial_manager__in=territorial_managers,
                regional_manager=f"{request.user.last_name} {request.user.first_name}",
            )
            .exclude(territorial_manager="UNKNOWN", regional_manager__isnull=True)
            .all()
        )

    managers = {}
    totals_tm = {}
    totals_rm = {}
    ukrainian_totals = {"Ukraine": {"attended": 0, "payments": 0, "enrolled": 0}}
    for report in client_manager_reports:
        if (
            report.total_attended == 0
            and report.total_enrolled == 0
            and report.total_payments == 0
        ):
            continue
        if (
            report.territorial_manager is not None
            and report.territorial_manager != "UNKNOWN"
        ):
            if report.territorial_manager in totals_tm:
                totals_tm[report.territorial_manager][
                    "attended"
                ] += report.total_attended
                totals_tm[report.territorial_manager][
                    "payments"
                ] += report.total_payments
                totals_tm[report.territorial_manager][
                    "enrolled"
                ] += report.total_enrolled
            else:
                totals_tm[report.territorial_manager] = {
                    "attended": report.total_attended,
                    "payments": report.total_payments,
                    "enrolled": report.total_enrolled,
                }
            if report.regional_manager in totals_rm:
                totals_rm[report.regional_manager]["attended"] += report.total_attended
                totals_rm[report.regional_manager]["payments"] += report.total_payments
                totals_rm[report.regional_manager]["enrolled"] += report.total_enrolled
            else:
                totals_rm[report.regional_manager] = {
                    "attended": report.total_attended,
                    "payments": report.total_payments,
                    "enrolled": report.total_enrolled,
                }
            ukrainian_totals["Ukraine"]["attended"] += report.total_attended
            ukrainian_totals["Ukraine"]["payments"] += report.total_payments
            ukrainian_totals["Ukraine"]["enrolled"] += report.total_enrolled

    for tm in territorial_managers:
        rm = get_rm_by_tm(tm)
        if rm is not None:
            if rm in managers:
                managers[rm].append(tm)
            else:
                managers[rm] = [tm]
    context = {
        "segment": "programming_new",
        "report_date_default": report_date_default,
        "username": request.user.username,
        "report_scales": possible_report_scales,
        "user_group": get_user_role(request.user),
        "location_reports": location_reports,
        "managers": managers,
        "client_manager_reports": client_manager_reports,
        "user_role": user_role,
        "totals_tm": totals_tm,
        "totals_rm": totals_rm,
        "ukrainian_totals": ukrainian_totals,
        # "reports_by_course": formatted_courses
    }
    html_template = loader.get_template(
        "logika_statistics/report_programming_updated.html"
    )
    return HttpResponse(html_template.render(context, request))


def get_rm_tm_by_tutor(tutor):
    location = Location.objects.filter(tutor=tutor).first()
    if not location:
        location = Location.objects.filter(tutor_english=tutor).first()
    return location.regional_manager, location.territorial_manager


def get_rm_by_tm(tm):
    location = Location.objects.filter(territorial_manager=tm).first()
    if location:
        return location.regional_manager
    else:
        return "None"


def get_rm_by_tutor_programming(tutor):
    location = Location.objects.filter(tutor=tutor).first()
    if location:
        return location.regional_manager
    else:
        return "None"


def get_rm_by_tutor_english(tutor):
    location = Location.objects.filter(tutor_english=tutor).first()
    if location:
        return location.regional_manager
    else:
        return "None"


def get_conversion(payments, attended):
    conversion = None
    if payments == 0 and attended == 0:
        conversion = 0
    else:
        try:
            conversion = round((payments / attended) * 100, 2)
        except ZeroDivisionError:
            conversion = 100
    return conversion if conversion else 0


@login_required(login_url="/login/")
def home(request):
    html_template = loader.get_template("logika_statistics/home_page.html")
    print(get_user_role(request.user))
    return HttpResponse(
        html_template.render(
            {
                "segment": "",
                "user_name": f"{request.user.first_name} {request.user.last_name}",
                "user_role": get_user_role(request.user),
            },
            request,
        )
    )


@login_required(login_url="/login/")
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:
        load_template = request.path.split("/")[-1]

        if load_template == "admin":
            return HttpResponseRedirect(reverse("admin:index"))
        context["segment"] = load_template

        html_template = loader.get_template("logika_statistics/" + load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:
        html_template = loader.get_template("logika_statistics/page-404.html")
        return HttpResponse(html_template.render(context, request))

    except:
        html_template = loader.get_template("logika_statistics/page-500.html")
        return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def edit_location(request, location_id):
    location = Location.objects.get(id=location_id)
    if request.method == "POST":
        form = UpdateLocationForm(request.POST, instance=location)
        if form.is_valid():
            form.save()
            return redirect("logika_statistics:list-locations")
    territorial_managers = TerritorialManagerProfile.objects.all()
    regional_managers = RegionalManagerProfile.objects.all()
    tutors = TutorProfile.objects.all()
    return render(
        request,
        template_name="logika_statistics/update_location.html",
        context={
            "location": location,
            "territorial_managers": territorial_managers,
            "regional_managers": regional_managers,
            "tutors": tutors,
        },
    )


@login_required(login_url="/login/")
def list_locations(request):
    locations = Location.objects.all()
    context = {
        "locations": locations,
    }
    html_template = loader.get_template("logika_statistics/list_locations.html")
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def delete_location(request, location_id):
    location = Location.objects.get(id=location_id)
    location.delete()
    return redirect("logika_statistics:list-locations")


@login_required(login_url="/login/")
def create_location(request):
    if request.method == "POST":
        form = UpdateLocationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("logika_statistics:list-locations")
    territorial_managers = TerritorialManagerProfile.objects.all()
    regional_managers = RegionalManagerProfile.objects.all()
    tutors = TutorProfile.objects.all()
    return render(
        request,
        template_name="logika_statistics/create_location.html",
        context={
            "territorial_managers": territorial_managers,
            "regional_managers": regional_managers,
            "tutors": tutors,
        },
    )
