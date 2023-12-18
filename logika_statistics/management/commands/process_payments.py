import os
from pathlib import Path

import requests
from django.core.management.base import BaseCommand
from dotenv import load_dotenv

import library
from logika_administrative.settings import BASE_DIR
from logika_statistics.models import MasterClassRecord, PaymentRecord, Location
from utils.lms_authentication import get_authenticated_session


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "-c", "--course", type=str, default=None, help="Course", dest="course"
        )

    @staticmethod
    def process_payment(paym):
        if paym is None:
            return 0
        if isinstance(paym, str):
            paym = paym.replace(".00", "").replace(",", "")
            return int(paym)
        else:
            return paym

    def handle(self, *args, **options):
        load_dotenv(Path(BASE_DIR, ".env"))
        lms_session = get_authenticated_session()
        start_date = os.environ.get("start_date")
        end_date = os.environ.get("end_date")
        url_start = start_date.replace("-", "")
        url_end = end_date.replace("-", "")
        course = (
            "Школы Программирования"
            if options["course"] == "programming"
            else "english"
        )
        if os.environ.get("ENVIRONMENT") == "development":
            one_c_host = "school.cloud24.com.ua"
        else:
            one_c_host = "localhost"
        url = f"https://{one_c_host}:22443/SCHOOL/ru_RU/hs/1cData/B2C/?from={url_start}&till={url_end}&businessDirection={course}&firstPayment=true"

        response = requests.get(url, headers=library.payments_headers, verify=False)
        payments_data = response.json()
        for payment in payments_data:
            student_id = payment["КлиентID_БО"]
            business = (
                "programming"
                if payment["НаправлениеБизнеса"] == "Школы программирования"
                else "english"
            )
            if self.process_payment(payment["Оплата"]) < 500:
                print(f"ISSUE: too small payment {str(payment['КлиентID_БО'])}")

            existing_report = (
                MasterClassRecord.objects.filter(
                    student_lms_id=student_id, business=business, attended=True
                )
                .order_by("start_date")
                .last()
            )
            if existing_report:
                report = PaymentRecord(
                    student_lms_id=existing_report.student_lms_id,
                    student_lms_name=existing_report.student_lms_name,
                    recent_group_lms_id=existing_report.mc_lms_id,
                    start_date=start_date,
                    end_date=end_date,
                    business=business,
                    location=existing_report.location,
                    teacher=existing_report.teacher,
                    teacher_lms_id=existing_report.teacher_lms_id,
                    client_manager=existing_report.client_manager,
                    territorial_manager=existing_report.territorial_manager,
                    regional_manager=existing_report.regional_manager,
                    course_title=existing_report.course_title,
                    course_id=existing_report.course_id,
                    payment_amount=self.process_payment(payment["Оплата"]),
                )
                report.save()
                continue
            url = f"https://lms.logikaschool.com/api/v2/student/default/view/{student_id}?id={student_id}&expand=lastGroup%2Cwallet%2Cbranch%2ClastGroup.branch%2CamoLead%2Cgroups%2Cgroups.b2bPartners"
            student_details_response = lms_session.get(url)
            if student_details_response.status_code == 404:
                print(f"ISSUE: student {student_id} not found in LMS")
                continue
            student_details = student_details_response.json()["data"]
            student_lms_name = student_details.get("fullName")
            student_lms_id = student_details.get("id")
            student_recent_group = student_details.get("lastGroup")
            if student_recent_group is None:
                print(f"ISSUE: student {student_id} has no recent group")
            student_recent_group_id = student_recent_group.get("id")

            group_data_url = f"https://lms.logikaschool.com/api/v1/group/{student_recent_group_id}?expand=venue,teacher,curator"
            group_data_response = lms_session.get(group_data_url)
            if group_data_response.status_code != 200:
                print(
                    f"ISSUE: group {student_recent_group_id} unable to retrieve from LMS"
                )
                continue
            group_data = group_data_response.json()["data"]
            group_teacher_data = group_data.get("teacher")
            group_venue_data = group_data.get("venue")
            group_curator_data = group_data.get("curator")
            group_course_data = group_data.get("course")

            if group_teacher_data is None:
                print(f"ISSUE: group {student_recent_group_id} has no teacher")

            if group_venue_data is None:
                print(f"ISSUE: group {student_recent_group_id} has no venue")

            if group_curator_data is None:
                print(f"ISSUE: group {student_recent_group_id} has no curator")

            location = group_venue_data.get("title") if group_venue_data else None
            teacher = group_teacher_data.get("name") if group_teacher_data else None
            teacher_lms_id = (
                group_teacher_data.get("id") if group_teacher_data else None
            )
            client_manager = (
                group_curator_data.get("name") if group_curator_data else None
            )
            course_title = group_course_data.get("name") if group_course_data else None
            course_id = group_course_data.get("id") if group_course_data else None
            course_business = (
                library.get_business_by_group_course_id(course_id)
                if course_id
                else None
            )
            if course_business != business:
                print(
                    f"ISSUE: student {student_id} has wrong business {course_business}"
                )

            location_object = Location.objects.filter(
                lms_location_name=location
            ).first()
            if location_object is None:
                print(f"ISSUE: location {location} not found in DB")

            territorial_manager = None
            regional_manager = None

            if location_object:
                territorial_manager = location_object.territorial_manager
                regional_manager = location_object.regional_manager

            report = PaymentRecord(
                student_lms_id=student_lms_id,
                student_lms_name=student_lms_name,
                recent_group_lms_id=student_recent_group_id,
                start_date=start_date,
                end_date=end_date,
                business=business,
                location=location,
                teacher=teacher,
                teacher_lms_id=teacher_lms_id,
                client_manager=client_manager,
                territorial_manager=territorial_manager,
                regional_manager=regional_manager,
                course_title=course_title,
                course_id=course_id,
                payment_amount=self.process_payment(payment["Оплата"]),
            )
            report.save()
