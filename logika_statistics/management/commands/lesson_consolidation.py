import csv
import os
import pickle
from datetime import datetime
from pathlib import Path

import pandas as pd
from django.core.management.base import BaseCommand

from logika_administrative.settings import BASE_DIR
from logika_statistics.models import ConsolidationReport
from utils.lms_authentication import get_authenticated_session


class Command(BaseCommand):
    def __init__(self):
        super().__init__(self)
        self.start_date = os.environ.get("start_date")
        self.end_date = os.environ.get("end_date")
        self.session = get_authenticated_session()
        self.royalty_csv_path = Path(
            BASE_DIR, "reports", f"royalty_{self.start_date}_{self.end_date}.csv"
        )
        self.royalty_1c_path = Path(BASE_DIR, "reports", "consolidation_report.xlsx")
        self.parsed_start_date = datetime.strptime(self.start_date, "%Y-%m-%d")
        self.parsed_end_date = datetime.strptime(self.end_date, "%Y-%m-%d")
        self.group_data_path = Path(BASE_DIR, "groups_attendance_data")

    def download_royalty_csv(self):
        if not self.royalty_csv_path.exists():
            royalty_url = (
                f"https://lms.logikaschool.com/stats/royalty/download?"
                f"startDate={self.start_date}&endDate={self.end_date}"
            )
            with self.session.get(royalty_url) as response:
                with self.royalty_csv_path.open("wb") as f:
                    f.write(response.content)

    def handle(self, *args, **options):
        self.download_royalty_csv()
        if not self.group_data_path.exists():
            groups_attendance_data = {}
            with open(self.royalty_csv_path, "r", encoding="utf-8") as f:
                csv_reader = csv.reader(f, delimiter=";")
                
                for line, group_row in enumerate(csv_reader):
                    try:
                        if line == 0:
                            continue

                        if group_row[3] == "masterclass":
                            continue

                        group_id = group_row[1]
                        if group_id in groups_attendance_data:
                            continue
                        group_data_url = f"https://lms.logikaschool.com/api/v1/group/{group_id}?expand=venue,curator"
                        group_data_response = self.session.get(group_data_url)
                        if group_data_response.status_code != 200:
                            print(
                                f"ERROR getting group from lms: {group_data_response.status_code} {group_data_url}"
                            )
                            continue
                        group_data = group_data_response.json()["data"]
                        group_attendance_url = f"https://lms.logikaschool.com/api/v1/stats/default/attendance?group={group_id}"
                        group_attendance_response = self.session.get(group_attendance_url)
                        if group_attendance_response.status_code != 200:
                            print(
                                f"ERROR getting attendance from lms: "
                                f"{group_attendance_response.status_code} {group_attendance_url}"
                            )
                            continue
                        group_attendance = group_attendance_response.json()["data"]
                        group_curator = (
                            group_data["curator"]["name"] if group_data["curator"] else ""
                        )
                        group_venue = (
                            group_data["venue"]["title"] if group_data["venue"] else ""
                        )
                        group_title = group_row[2]
                        print(f"Got group {group_title} {group_id}")

                        groups_attendance_data[group_id] = {}
                        groups_attendance_data[group_id]["lms"] = {}
                        for student in group_attendance:
                            student_id = student["student_id"]
                            groups_attendance_data[group_id]["lms"][student_id] = 0
                            for lesson in student["attendance"]:
                                parsed_date = datetime.strptime(
                                    lesson["start_time_formatted"][3:], "%d.%m.%y %H:%M"
                                )
                                if (
                                    self.parsed_start_date
                                    <= parsed_date
                                    <= self.parsed_end_date
                                ):
                                    if lesson["status"] not in ["present", "absent"]:
                                        continue
                                    groups_attendance_data[group_id]["lms"][student_id] += 1
                            print(
                                f"Processed student {student_id}, "
                                f"{group_id}, "
                                f"student_attendance: "
                                f"{groups_attendance_data[group_id]['lms'][student_id]}"
                            )

                        groups_attendance_data[group_id]["group_title"] = group_title
                        groups_attendance_data[group_id]["group_curator"] = group_curator
                        groups_attendance_data[group_id]["group_venue"] = group_venue
                    except Exception as exp:
                        print(exp)
            with open(self.group_data_path, "wb") as groups_data_file:
                pickle.dump(groups_attendance_data, groups_data_file)

        # collecting data from 1c
        with open(self.group_data_path, "rb") as groups_data_file:
            groups_attendance_data = pickle.load(groups_data_file)

        unused_columns = [1, 2, 4, 6, 7, 8, 9]
        payments_dataset = pd.read_excel(
            self.royalty_1c_path, sheet_name="TDSheet", skiprows=4
        )
        payments_dataset = payments_dataset.drop(
            payments_dataset.columns[unused_columns], axis=1
        )
        payments_dataset.rename(
            columns={
                "Unnamed: 0": "location",
                "Unnamed: 3": "student, id",
                "Unnamed: 5": "group, id",
                "Количество учеников.3": "amount",
            },
            inplace=True,
        )
        payments_dataset[["student_name", "student_id", "trash"]] = payments_dataset[
            "student, id"
        ].str.split(", ", expand=True)
        payments_dataset[["group_name", "group_id", "trash"]] = payments_dataset[
            "group, id"
        ].str.split(", ", expand=True)
        payments_dataset["group_id"] = payments_dataset["group_id"].str.replace(",", "")
        unique_group_ids = payments_dataset["group_id"].unique()
        for group_id in unique_group_ids:
            group_df = payments_dataset[payments_dataset["group_id"] == group_id]
            if group_id not in groups_attendance_data:
                groups_attendance_data[group_id] = {"lms": None, "one_c": {}}
            else:
                groups_attendance_data[group_id]["one_c"] = {}
            for idx, student in group_df.iterrows():
                if groups_attendance_data[group_id]["lms"] is None:
                    groups_attendance_data[group_id]["group_title"] = student[
                        "group_name"
                    ]
                    groups_attendance_data[group_id]["group_curator"] = "Невідомий КМ"
                    groups_attendance_data[group_id]["group_venue"] = student[
                        "location"
                    ]
                try:
                    int(student["student_id"])
                except:
                    ConsolidationReport.objects.create(
                        group_id=group_id,
                        student_id="",
                        type="Помилка з ID студента",
                        comment=f"Некоректний або відсутній ID студента {student['student_name']} в 1С",
                        payment_total=0,
                        lms_total=0,
                        difference=0,
                        location=student["location"],
                        group_title=student["group_name"],
                        start_date=self.start_date,
                        end_date=self.end_date,
                    )
                    continue

                groups_attendance_data[group_id]["one_c"][
                    int(student["student_id"])
                ] = student["amount"]
        # defining difference and comment

        for group_id, group_data in groups_attendance_data.items():
            group_comment = ""

            if group_data.get("lms") is None or group_data.get("lms") == {}:
                group_comment += "Група відсутня в LMS. "
                group_data["lms"] = {}
            if group_data.get("one_c") is None or group_data.get("one_c") == {}:
                group_comment += "Група відсутня в 1С. "
                group_data["one_c"] = {}

            lms_minus_one_c = list(
                set(group_data["lms"].keys()) - set(group_data["one_c"].keys())
            )
            for student_id in lms_minus_one_c:
                student_comment = f"Учень {student_id} відсутній в 1С. "
                type = "Відсутній в 1С"
                ConsolidationReport.objects.create(
                    group_id=group_id,
                    student_id=student_id,
                    type=type,
                    comment=group_comment + student_comment,
                    payment_total=0,
                    lms_total=group_data["lms"][student_id],
                    difference=group_data["lms"][student_id],
                    location=group_data["group_venue"],
                    group_title=group_data["group_title"],
                    start_date=self.start_date,
                    end_date=self.end_date,
                )
            one_c_minus_lms = list(
                set(group_data["one_c"].keys()) - set(group_data["lms"].keys())
            )
            for student_id in one_c_minus_lms:
                student_comment = f"Учень {student_id} відсутній в LMS. "
                type = "Відсутній в LMS"
                ConsolidationReport.objects.create(
                    group_id=group_id,
                    student_id=student_id,
                    type=type,
                    comment=group_comment + student_comment,
                    payment_total=group_data["one_c"][student_id],
                    lms_total=0,
                    difference=group_data["one_c"][student_id],
                    location=group_data["group_venue"],
                    group_title=group_data["group_title"],
                    start_date=self.start_date,
                    end_date=self.end_date,
                )

            for student_id, student_data in group_data["lms"].items():
                student_comment = ""

                if student_id in lms_minus_one_c and student_data != 0:
                    continue

                if student_id in one_c_minus_lms and student_data != 0:
                    continue

                if student_id in lms_minus_one_c and student_data == 0:
                    continue

                if student_data != group_data["one_c"][student_id]:
                    if student_data > group_data["one_c"][student_id]:
                        student_comment += f"В LMS більше списань, ніж в 1С. "
                        type = "Більше списань в LMS"
                        difference = student_data - group_data["one_c"][student_id]
                        ConsolidationReport.objects.create(
                            group_id=group_id,
                            student_id=student_id,
                            type=type,
                            comment=group_comment + student_comment,
                            payment_total=group_data["one_c"][student_id],
                            lms_total=student_data,
                            difference=difference,
                            location=group_data["group_venue"],
                            group_title=group_data["group_title"],
                            start_date=self.start_date,
                            end_date=self.end_date,
                        )
                        continue
                    else:
                        student_comment += f"В 1С більше списань, ніж в LMS. "
                        type = "Більше списань в 1С"
                        difference = group_data["one_c"][student_id] - student_data
                        ConsolidationReport.objects.create(
                            group_id=group_id,
                            student_id=student_id,
                            type=type,
                            comment=group_comment + student_comment,
                            payment_total=group_data["one_c"][student_id],
                            lms_total=student_data,
                            difference=difference,
                            location=group_data["group_venue"],
                            group_title=group_data["group_title"],
                            start_date=self.start_date,
                            end_date=self.end_date,
                        )
