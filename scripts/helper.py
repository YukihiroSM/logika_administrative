from django.core import management
from logika_administrative.settings import BASE_DIR
import os
import logging
import datetime
from pathlib import Path
import json
from logika_statistics.models import StudentReport, Location
from utils.lms_authentication import get_authenticated_session
from concurrent.futures import ThreadPoolExecutor
import pandas as pd

session = get_authenticated_session()
start_date = "2023-12-04"
end_date = "2023-12-10"
updated_students_count = 0


def process_one_group(group_id):
    print(f"Starting processing {str(group_id)}" + " " + str(datetime.datetime.now()))
    group_data_url = f"https://lms.logikaschool.com/api/v1/group/{group_id}?expand=venue%2Cteacher%2Ccurator%2Cbranch"
    resp = session.get(group_data_url)
    if resp.status_code == 200:
        group_title = resp.json()["data"]["title"].lower()
        if "ук" in group_title and not ("мк" in group_title):
            print(group_title)
            students_link = f"https://lms.logikaschool.com/api/v2/group/student/index?groupId={group_id}&expand=lastGroup%2ClastGroup.invoices%2ClastGroup.invoices.invoiceMail%2Cbranch%2Cwallet%2CamoLead%2Cb2bPartners%2Cgroups.b2bPartners"
            students_resp = session.get(students_link)
            if students_resp.status_code == 200:
                students_data = students_resp.json()["data"]["items"]
                for student in students_data:
                    if student["lastGroup"]["id"] != group_id:
                        redirected_student_link = f"https://lms.logikaschool.com/api/v2/student/default/view/{student['id']}?id={student['id']}&expand=lastGroup%2Cwallet%2Cbranch%2ClastGroup.branch%2CamoLead%2Cgroups%2Cgroups.b2bPartners"
                        redirected_student_resp = session.get(redirected_student_link)
                        if redirected_student_resp.status_code == 200:
                            print("Inside redirected student")
                            redirected_student_data = redirected_student_resp.json()[
                                "data"
                            ]
                            student_groups = redirected_student_data["groups"]
                            for number, group in enumerate(student_groups):
                                if group["id"] == group_id:
                                    break
                            if number != len(student_groups) - 1:
                                next_group_index = number + 1
                                next_group_id = student_groups[next_group_index]["id"]
                                next_group_link = f"https://lms.logikaschool.com/api/v1/group/{next_group_id}?expand=venue%2Cteacher%2Ccurator%2Cbranch"
                                next_group_resp = session.get(next_group_link)
                                if next_group_resp.status_code == 200:
                                    print(f"Inside next group {next_group_id}")
                                    next_group_type = next_group_resp.json()["data"][
                                        "type"
                                    ]["value"]
                                    print(next_group_type)
                                    if next_group_type != "regular":
                                        continue
                                    print(f"Next group {next_group_id} is regular!")
                                attendance_link = f"https://lms.logikaschool.com/api/v1/stats/default/attendance?group={next_group_id}&students%5B%5D={student['id']}"
                                attendance_resp = session.get(attendance_link)
                                if attendance_resp.status_code == 200:
                                    print("Getting attendance")
                                    att_json = attendance_resp.json()
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
                                        lesson_datetime = lesson["start_time_formatted"]
                                        date_format = "%d.%m.%y %H:%M"
                                        date_object = datetime.datetime.strptime(
                                            lesson_datetime[3:], date_format
                                        )
                                        start_date_time = datetime.datetime.strptime(
                                            start_date, "%Y-%m-%d"
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
                                                student_report = (
                                                    StudentReport.objects.filter(
                                                        student_lms_id=student["id"],
                                                        start_date=start_date,
                                                        end_date=end_date,
                                                    ).first()
                                                )
                                                if student_report:
                                                    student_report.attended_mc = 1
                                                    student_report.save()
                                                    global updated_students_count
                                                    updated_students_count += 1
                                                else:
                                                    print(
                                                        f"NO STUDENT REPORT FOR {student['id']}"
                                                    )


def parse_students_in_groups(group_ids):
    i = 1
    for group_id in group_ids:
        print(
            f"Processing {str(group_id)} ({str(i)}/{str(len(group_ids))})"
            + " "
            + str(datetime.datetime.now())
        )
        process_one_group(group_id)
        i += 1


def parse_in_threads(group_ids):
    num_of_threads = 1
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
        executor.map(parse_students_in_groups, args)


def run():
    month = "Лютий"
    collect_groups_link = f"https://lms.logikaschool.com/group/default/schedule?GroupLessonSearch%5Bstart_time%5D={start_date}+-+{end_date}&GroupLessonSearch%5Bgroup_id%5D=&GroupLessonSearch%5Bgroup.title%5D=&GroupLessonSearch%5Bgroup.venue%5D=&GroupLessonSearch%5Bgroup.active_student_count%5D=&GroupLessonSearch%5Bteacher.name%5D=&GroupLessonSearch%5Bgroup.curator.name%5D=&GroupLessonSearch%5Bgroup.type%5D=&GroupLessonSearch%5Bgroup.type%5D%5B%5D=masterclass&GroupLessonSearch%5Bgroup.course.name%5D=&GroupLessonSearch%5Bgroup.branch.title%5D=&export=true&name=default&exportType=csv"
    response = session.get(collect_groups_link)
    output_file_path = Path(
        BASE_DIR, "lms_reports", month, f"{start_date}_{end_date}", "schedule_cl.csv"
    )
    with open(output_file_path, "w", encoding="UTF-8") as file_obj:
        for line in response.text:
            file_obj.write(line)
    print("Got groups from lms. Written to file." + " " + str(datetime.datetime.now()))
    mk_df = pd.read_csv(output_file_path, delimiter=";")
    mk_df = mk_df.drop(
        [
            "Время след. урока",
            "S Статус урока",
            "Уч-ки",
            " Отчисленные и переведенные",
            "Тип группы",
            "Присутствовали",
        ],
        axis=1,
    )
    mk_df.rename(
        columns={
            "Group ID": "group_id",
            "Название группы": "group_name",
            "Площадка": "group_location",
            "Преп. на занятии": "group_teacher",
            "Куратор": "client_manager",
            "Курс": "course",
            "Офис": "region",
        },
        inplace=True,
    )
    mk_df = mk_df.where(pd.notnull(mk_df), None)
    mk_df.replace("", None, inplace=True)
    group_ids = list(set(mk_df["group_id"].tolist()))
    parse_students_in_groups(group_ids)
    print(f"Total updated students_count: {updated_students_count}")
