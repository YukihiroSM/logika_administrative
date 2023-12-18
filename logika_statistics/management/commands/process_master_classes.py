import datetime
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pandas as pd
from django.core.management.base import BaseCommand

from library import get_business_by_group_course_id
from logika_administrative.settings import BASE_DIR
from logika_statistics.models import MasterClassRecord, Location
from utils.lms_authentication import get_authenticated_session


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.session = get_authenticated_session()
        self.failed_groups = []

    def process_one_group(self, group_id):
        try:
            start_date = os.environ.get("start_date")
            end_date = os.environ.get("end_date")
            group_data_url = f"https://lms.logikaschool.com/api/v1/group/{group_id}?expand=venue%2Cteacher%2Ccurator%2Cbranch"
            students_statistic_url = f"https://lms.logikaschool.com/api/v1/stats/default/attendance?group={group_id}"
            group_data_resp = self.session.get(group_data_url)
            students_statistic_resp = self.session.get(students_statistic_url)

            if not group_data_resp.ok or not students_statistic_resp.ok:
                self.failed_groups.append(group_id)
                return

            group_data = group_data_resp.json().get("data")
            students_statistics_data = students_statistic_resp.json().get("data")

            title = group_data["title"]
            venue = group_data["venue"]
            location_name = venue.get("title") if venue else None

            curator_info = group_data["curator"]
            curator_name = curator_info.get("name") if curator_info else None

            teacher_info = group_data["teacher"]
            teacher_name = teacher_info.get("name") if teacher_info else None
            teacher_id = teacher_info.get("id") if teacher_info else None

            course_data = group_data["course"]
            course_title = course_data.get("name") if course_data else None
            course_id = course_data.get("id") if course_data else None

            if not location_name:
                self.failed_groups.append(group_id)
                print(f"ISSUE: No location name for group {group_id}: {title}")

            if not curator_name:
                self.failed_groups.append(group_id)
                print(f"ISSUE: No curator name for group {group_id}: {title}")

            if not teacher_name:
                self.failed_groups.append(group_id)
                print(f"ISSUE: No teacher name for group {group_id}: {title}")

            if not course_title:
                self.failed_groups.append(group_id)
                print(f"ISSUE: No course name for group {group_id}: {title}")

            business = None
            if course_id:
                business = get_business_by_group_course_id(course_id)

            territorial_manager = None
            regional_manager = None
            tutor = None
            if location_name:
                location_obj = Location.objects.filter(
                    lms_location_name=location_name
                ).first()
                if location_obj:
                    territorial_manager = location_obj.territorial_manager
                    regional_manager = location_obj.regional_manager
                    tutor = location_obj.tutor
                else:
                    print(
                        f"ISSUE: No location with name {location_name} in the list of locations"
                    )

            if "ук" in title.lower() and not ("мк" in title.lower()):
                print("ATTENTION: Processing student in Lesson in Credit")
                students_link = f"https://lms.logikaschool.com/api/v2/group/student/index?groupId={group_id}&expand=lastGroup%2ClastGroup.invoices%2ClastGroup.invoices.invoiceMail%2Cbranch%2Cwallet%2CamoLead%2Cb2bPartners%2Cgroups.b2bPartners"
                students_resp = self.session.get(students_link)
                if students_resp.status_code == 200:
                    students_data = students_resp.json()["data"]["items"]

                    for student in students_data:
                        student_name = student["fullName"]
                        student_id = student["id"]
                        attended = False
                        if student["lastGroup"]["id"] != group_id:
                            redirected_student_link = f"https://lms.logikaschool.com/api/v2/student/default/view/{student['id']}?id={student['id']}&expand=lastGroup%2Cwallet%2Cbranch%2ClastGroup.branch%2CamoLead%2Cgroups%2Cgroups.b2bPartners"
                            redirected_student_resp = self.session.get(
                                redirected_student_link
                            )
                            if redirected_student_resp.status_code == 200:
                                print("Inside redirected student")
                                redirected_student_data = (
                                    redirected_student_resp.json()["data"]
                                )
                                student_groups = redirected_student_data["groups"]
                                for number, group in enumerate(student_groups):
                                    if group["id"] == group_id:
                                        break
                                if number != len(student_groups) - 1:
                                    next_group_index = number + 1
                                    next_group_id = student_groups[next_group_index][
                                        "id"
                                    ]
                                    next_group_link = f"https://lms.logikaschool.com/api/v1/group/{next_group_id}?expand=venue%2Cteacher%2Ccurator%2Cbranch"
                                    next_group_resp = self.session.get(next_group_link)
                                    if next_group_resp.status_code == 200:
                                        print(f"Inside next group {next_group_id}")
                                        next_group_type = next_group_resp.json()[
                                            "data"
                                        ]["type"]["value"]
                                        print(next_group_type)
                                        if next_group_type != "regular":
                                            continue
                                        print(f"Next group {next_group_id} is regular!")
                                    attendance_link = f"https://lms.logikaschool.com/api/v1/stats/default/attendance?group={next_group_id}&students%5B%5D={student['id']}"
                                    attendance_resp = self.session.get(attendance_link)
                                    if attendance_resp.status_code == 200:
                                        print("Getting attendance")
                                        try:
                                            student_attendance_data = (
                                                attendance_resp.json()["data"][0][
                                                    "attendance"
                                                ]
                                            )
                                        except IndexError:
                                            student_attendance_data = []
                                            print("Attendance is empty")
                                        for lesson in student_attendance_data:
                                            lesson_datetime = lesson[
                                                "start_time_formatted"
                                            ]
                                            date_format = "%d.%m.%y %H:%M"
                                            date_object = datetime.datetime.strptime(
                                                lesson_datetime[3:], date_format
                                            )
                                            start_date_time = (
                                                datetime.datetime.strptime(
                                                    start_date, "%Y-%m-%d"
                                                )
                                            )
                                            end_date_time = datetime.datetime.strptime(
                                                end_date, "%Y-%m-%d"
                                            )
                                            if (
                                                start_date_time
                                                <= date_object
                                                <= end_date_time
                                            ):
                                                student_status = lesson["status"]
                                                if student_status == "present":
                                                    attended = True
                                                else:
                                                    attended = False
                        new_record = MasterClassRecord(
                            student_lms_id=student_id,
                            student_lms_name=student_name,
                            mc_lms_id=group_id,
                            start_date=start_date,
                            end_date=end_date,
                            business=business,
                            location=location_name,
                            teacher=teacher_name,
                            teacher_lms_id=teacher_id,
                            tutor=tutor,
                            client_manager=curator_name,
                            territorial_manager=territorial_manager,
                            regional_manager=regional_manager,
                            course_title=course_title,
                            course_id=course_id,
                            attended=attended,
                            is_uk=True,
                        )
                        try:
                            new_record.save()
                        except Exception as exc:
                            print(exc)

            for student in students_statistics_data:
                student_id = student.get("student_id")
                student_attendance = student.get("attendance")[0]
                student_status = student_attendance.get("status")
                if student_status == "present":
                    attended = True
                else:
                    attended = False

                student_details_url = f"https://lms.logikaschool.com/api/v1/student/view/{student_id}?expand=branch,group"

                student_details_resp = self.session.get(student_details_url)

                if student_details_resp.status_code == 200:
                    student_data = student_details_resp.json()["data"]
                    student_name = student_data.get("full_name")

                    new_record = MasterClassRecord(
                        student_lms_id=student_id,
                        student_lms_name=student_name,
                        mc_lms_id=group_id,
                        start_date=start_date,
                        end_date=end_date,
                        business=business,
                        location=location_name,
                        teacher=teacher_name,
                        teacher_lms_id=teacher_id,
                        tutor=tutor,
                        client_manager=curator_name,
                        territorial_manager=territorial_manager,
                        regional_manager=regional_manager,
                        course_title=course_title,
                        course_id=course_id,
                        attended=attended,
                        is_uk=False,
                    )
                    try:
                        new_record.save()
                    except Exception as exc:
                        print(exc)

            print(
                f"Got group with ID {group_id},\n"
                f"Title: {title},\n"
                f"Location Name: {location_name},\n"
                f"Manager Name: {curator_name},\n"
                f"Teacher Name: {teacher_name},\n"
                f"Course Title: {course_title}"
            )
        except Exception as exc:
            print(exc)
            return

    def parse_students_in_groups(self, group_ids):
        i = 1
        for group_id in group_ids:
            print(
                f"Processing {str(group_id)} ({str(i)}/{str(len(group_ids))})"
                + str(datetime.datetime.now())
            )
            self.process_one_group(group_id)
            i += 1

    def parse_in_threads(self, group_ids):
        num_of_threads = 6
        if num_of_threads == 0:
            num_of_threads = 1
        separator = len(group_ids) // num_of_threads
        args = []
        for i in range(0, num_of_threads):
            if i == num_of_threads - 1:
                arg = group_ids[i * separator :]
            else:
                arg = group_ids[i * separator : (i + 1) * separator]
            args.append(arg)
        with ThreadPoolExecutor(max_workers=num_of_threads) as executor:
            executor.map(self.parse_students_in_groups, args)

    def handle(self, *args, **options):
        start_date = os.environ.get("start_date")
        end_date = os.environ.get("end_date")
        print("Starting getting groups from LMS" + " " + str(datetime.datetime.now()))
        output_file_path = Path(
            BASE_DIR, "reports", f"{start_date}_{end_date}", "schedule.csv"
        )
        if not os.path.exists(output_file_path):
            os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
            collect_groups_link = f"https://lms.logikaschool.com/group/default/schedule?GroupLessonSearch%5Bstart_time%5D={start_date}+-+{end_date}&GroupLessonSearch%5Bgroup_id%5D=&GroupLessonSearch%5Bgroup.title%5D=&GroupLessonSearch%5Bgroup.venue%5D=&GroupLessonSearch%5Bgroup.active_student_count%5D=&GroupLessonSearch%5Bteacher.name%5D=&GroupLessonSearch%5Bgroup.curator.name%5D=&GroupLessonSearch%5Bgroup.type%5D=&GroupLessonSearch%5Bgroup.type%5D%5B%5D=masterclass&GroupLessonSearch%5Bgroup.course.name%5D=&GroupLessonSearch%5Bgroup.branch.title%5D=&export=true&name=default&exportType=csv"
            response = self.session.get(collect_groups_link)
            with open(output_file_path, "w", encoding="UTF-8") as file_obj:
                for line in response.text:
                    file_obj.write(line)

        print(
            "Got groups from lms. Written to file." + " " + str(datetime.datetime.now())
        )
        mk_df = pd.read_csv(output_file_path, delimiter=";")
        mk_df = mk_df[["Group ID"]]
        mk_df = mk_df.where(pd.notnull(mk_df), None)
        mk_df.replace("", None, inplace=True)
        group_ids = list(set(mk_df["Group ID"].tolist()))
        self.parse_in_threads(group_ids)
