import datetime
import os
from abc import ABC, abstractmethod
from typing import Type, Optional
from urllib.parse import quote

from logika_teachers.repositories.dtos import MKReportDTO, MasterClassDTO, FailRecordDTO
from logika_teachers.repositories.error_record_repository import FailRecordRepositoryInterface
from logika_teachers.repositories.master_class_repository import MasterClassRepositoryInterface, MasterClassRepository
from logika_teachers.services.django_setup import *

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from library import get_business_by_group_course_id
from logika_administrative.settings import BASE_DIR
from logika_statistics.models import Location, MasterClassRecord
from logika_teachers.services.lms_service import LMSServiceInterface, LMSService
from utils.get_jwt_session import AutoRefreshJWTSession
from utils.lms_authentication import get_authenticated_session

import pandas as pd
import logging

logger = logging.getLogger("info_logger")


class MasterClassServiceInterface(ABC):
    __servicename__ = "default"

    def __init__(self, lms_service: Type[LMSServiceInterface], mk_repository: Type[MasterClassRepositoryInterface],
                 fail_repository: Type[FailRecordRepositoryInterface],
                 ban=False):
        self.start_date = None
        self.end_date = None
        self.lms_service = lms_service
        self.mk_repository = mk_repository
        self.fail_repository = fail_repository
        self.ban = ban
        self.failed_mk = {"request error": list(),
                          "location not found": list(),
                          "location name not specified": list(),
                          "other": list()}

    def add_fail_group(self, error_type: str, msg: str, **additional_filters):
        fail_list = self.failed_mk.get(error_type, None)
        if fail_list is None:
            logger.error(f"Incorrect fail record type ({error_type})")
            return
        additional_filters.update({"service": "master_class"})
        fail_dto = FailRecordDTO(error_type=error_type, error_msg=msg, additional_filters=additional_filters)
        fail_list.append(fail_dto)
        self.fail_repository.create_error_record(fail_dto)
        logger.debug("Fail group added")

    @abstractmethod
    def collect_master_classes(self, start_date: str, end_date: str):
        pass

    @abstractmethod
    def get_master_class_report(self, start_date: datetime.datetime) -> list:
        pass


class MasterClassService(MasterClassServiceInterface):
    __servicename__ = "Old LMS Service"
    _lms_session = get_authenticated_session()

    def collect_master_classes(self, start_date: str, end_date: str):
        if self.ban:
            logger.info(f"Collecting {self.__servicename__} banned")
            return
        self.start_date = start_date
        self.end_date = end_date
        logger.info(f"Collecting mk in {self.__servicename__}")
        self._clear_records()
        file_path = self._get_groups_data()
        self._process_dataframe_in_threads(file_path)

    def get_master_class_report(self, start_date: datetime.datetime) -> list:
        return self.mk_repository.get_master_class_statistics(start_date, business="programming", new_lms=False)

    def _clear_records(self):
        MasterClassRecord.objects.filter(start_date=self.start_date, end_date=self.end_date, new_lms=False).delete()

    def _get_groups_data(self) -> Path:
        collect_groups_link = f"https://lms.logikaschool.com/group/default/schedule?GroupLessonSearch%5Bstart_time%5D={self.start_date}+-+{self.end_date}&GroupLessonSearch%5Bgroup_id%5D=&GroupLessonSearch%5Bgroup.title%5D=&GroupLessonSearch%5Bgroup.venue%5D=&GroupLessonSearch%5Bgroup.active_student_count%5D=&GroupLessonSearch%5Bteacher.name%5D=&GroupLessonSearch%5Bgroup.curator.name%5D=&GroupLessonSearch%5Bgroup.type%5D=&GroupLessonSearch%5Bgroup.type%5D%5B%5D=masterclass&GroupLessonSearch%5Bgroup.course.name%5D=&GroupLessonSearch%5Bgroup.branch.title%5D=&export=true&name=default&exportType=csv"
        output_file_path = BASE_DIR / "reports" / f"{self.start_date}_{self.end_date}" / "schedule.csv"
        folder_path = os.path.dirname(output_file_path)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        url = collect_groups_link
        response = self._lms_session.get(url)
        with open(output_file_path, "w", encoding="UTF-8") as file_obj:
            for line in response.text:
                file_obj.write(line)
        logger.info("SUCCESS: Groups file created")
        return output_file_path

    def _process_dataframe_in_threads(self, file_path: Path, max_threads=6):
        df = pd.read_csv(file_path, delimiter=';')
        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            futures = [executor.submit(self._process_group, row) for _, row in df.iterrows()]

    def _process_group(self, group: pd.Series):
        group_id = group["Group ID"]
        logger.info(f"Start process group: {group_id}")
        title = group["Назва групи"]
        location_name = group["Майданчик"]
        students_attendance_url = f"https://lms.logikaschool.com/api/v1/stats/default/attendance?group={group_id}"
        detail_group, status = self.lms_service.get_group(group_id)
        response = self._lms_session.get(students_attendance_url)
        course_id = detail_group.course_id

        business = get_business_by_group_course_id(course_id)
        territorial_manager = None
        regional_manager = None
        tutor = None
        if location_name:
            location = Location.objects.filter(lms_location_name=location_name).first()
            if location:
                territorial_manager = location.territorial_manager
                regional_manager = location.regional_manager
                tutor = location.tutor
            else:
                logger.error(f"Location {location_name} not found in DB")
                self.add_fail_group(error_type="location not found",
                                    msg=f"Локація {location_name} не знайдена у базі даних. Група {group_id} ({title})",
                                    regional_manager=regional_manager)
        else:
            logger.error("Location name not specified")
            self.add_fail_group(error_type="location name not specified",
                                msg=f"Локація {location_name} не знайдена у даних від БО. Група {group_id} ({title})",
                                regional_manager=regional_manager)

        if "ук" in title.lower() and not ("мк" in title.lower()):
            logger.warning("Processing student in Lesson in Credit")
            students_link = f"https://lms.logikaschool.com/api/v2/group/student/index?groupId={group_id}&expand=lastGroup%2ClastGroup.invoices%2ClastGroup.invoices.invoiceMail%2Cbranch%2Cwallet%2CamoLead%2Cb2bPartners%2Cgroups.b2bPartners"
            students_resp = self._lms_session.get(students_link)
            if students_resp.status_code == 200:
                students_data = students_resp.json()["data"]["items"]

                for student in students_data:
                    student_name = student["fullName"]
                    student_id = student["id"]
                    attended = False
                    if student["lastGroup"]["id"] != group_id:
                        redirected_student_link = f"https://lms.logikaschool.com/api/v2/student/default/view/{student['id']}?id={student['id']}&expand=lastGroup%2Cwallet%2Cbranch%2ClastGroup.branch%2CamoLead%2Cgroups%2Cgroups.b2bPartners"
                        redirected_student_resp = self._lms_session.get(
                            redirected_student_link
                        )
                        if redirected_student_resp.status_code == 200:
                            logger.info("Inside redirected student")
                            redirected_student_data = (
                                redirected_student_resp.json()["data"]
                            )
                            student_groups = redirected_student_data["groups"]
                            number = 0
                            for number, group in enumerate(student_groups):
                                if group["id"] == group_id:
                                    break
                            if number != len(student_groups) - 1:
                                next_group_index = number + 1
                                next_group_id = student_groups[next_group_index][
                                    "id"
                                ]
                                next_group_link = f"https://lms.logikaschool.com/api/v1/group/{next_group_id}?expand=venue%2Cteacher%2Ccurator%2Cbranch"
                                next_group_resp = self._lms_session.get(next_group_link)
                                if next_group_resp.status_code == 200:
                                    logger.info(f"Inside next group {next_group_id}")
                                    next_group_type = next_group_resp.json()[
                                        "data"
                                    ]["type"]["value"]
                                    if next_group_type != "regular":
                                        continue
                                    logger.info(f"Next group {next_group_id} is regular!")
                                attendance_link = f"https://lms.logikaschool.com/api/v1/stats/default/attendance?group={next_group_id}&students%5B%5D={student['id']}"
                                attendance_resp = self._lms_session.get(attendance_link)
                                if attendance_resp.status_code == 200:
                                    logger.info("Getting attendance")
                                    try:
                                        student_attendance_data = (
                                            attendance_resp.json()["data"][0][
                                                "attendance"
                                            ]
                                        )
                                    except IndexError:
                                        student_attendance_data = []
                                        logger.warning("Attendance is empty")
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
                                                self.start_date, "%Y-%m-%d"
                                            )
                                        )
                                        end_date_time = datetime.datetime.strptime(
                                            self.end_date, "%Y-%m-%d"
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
                    try:
                        mk_dto = MasterClassDTO(
                            student_lms_id=student_id,
                            student_lms_name=student_name,
                            mc_lms_id=group_id,
                            start_date=self.start_date,
                            end_date=self.end_date,
                            business=business,
                            location=location_name,
                            teacher="Placeholder",
                            teacher_lms_id=0,
                            tutor=tutor,
                            client_manager="Placeholder",
                            territorial_manager=territorial_manager,
                            regional_manager=regional_manager,
                            course_title="Placeholder",
                            course_id=course_id,
                            attended=attended,
                            is_uk=True,
                        )
                        self.mk_repository.get_or_create(mk_dto)
                    except Exception as exp:
                        logger.error(exp)
        if not response.ok:
            logger.error(f"Request error: {response.status_code}")
            self.add_fail_group(error_type="request error",
                                msg=f"Не вдалось отримати інформацію по студентам групи {group_id} ({title})",
                                regional_manager=regional_manager)
            return
        data = response.json().get("data")
        for item in data:
            student_id = item["student_id"]
            attendance = item["attendance"]
            attended = attendance[0].get("status") == "present"
            mk_dto = MasterClassDTO(
                student_lms_id=student_id,
                student_lms_name="Placeholder",
                mc_lms_id=group_id,
                start_date=self.start_date,
                end_date=self.end_date,
                business=business,
                location=location_name,
                teacher="Placeholder",
                teacher_lms_id=0,
                tutor=tutor,
                client_manager="Placeholder",
                territorial_manager=territorial_manager,
                regional_manager=regional_manager,
                course_title="Placeholder",
                course_id=course_id,
                attended=attended,
                is_uk=False,
            )
            mk_obj, created = self.mk_repository.get_or_create(mk_dto)
            logger.info(f"SUCCESS: Student in {group_id} processed {created}")
        logger.info(f"SUCCESS: Group {group_id} processed")


class MasterClassBOService(MasterClassServiceInterface):
    __servicename__ = "New LMS Service"
    _api_root = "https://api.logikaschool.com.ua"
    _lms_session = AutoRefreshJWTSession()

    def collect_master_classes(self, start_date: str, end_date: str):
        if self.ban:
            logger.info(f"Collecting {self.__servicename__} banned")
            return
        self.start_date = start_date
        self.end_date = end_date
        logger.info(f"Collecting mk in {self.__servicename__}")
        self._clear_records()
        groups_data = self._get_groups_data()
        if not groups_data:
            raise Exception("ERROR: Groups data does not got")
        self._process_groups_in_threads(groups_data)

    def get_master_class_report(self, start_date: datetime.datetime) -> list:
        return self.mk_repository.get_master_class_statistics(start_date, business="programming", new_lms=True)

    def _clear_records(self):
        MasterClassRecord.objects.filter(start_date=self.start_date, end_date=self.end_date, new_lms=True).delete()

    def _format_date_for_url(self, date_str: str) -> str:
        date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d")
        date_formatted = date_obj.strftime("%Y-%m-%dT%H:%M:%S")
        return date_formatted

    def _get_groups_data(self) -> Optional[list[dict]]:
        start_date = self._format_date_for_url(self.start_date)
        end_date = self._format_date_for_url(self.end_date)
        groups_response = self._lms_session.get(f"{self._api_root}/sync/statistics/group",
                                                params={"startDate": str(start_date),
                                                        "endDate": str(end_date),
                                                        "type": "MASTER_CLASS"})
        if groups_response.status_code != 200:
            logger.error(f"New LMS API request error: {groups_response.status_code} {groups_response.json()}")
            return None

        groups_data = groups_response.json()
        return groups_data

    def _process_groups_in_threads(self, groups_data: list[dict], max_threads=6):
        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            futures = [executor.submit(self._process_group, group.get("id", -1)) for group in groups_data]

    def _process_group(self, group_id: int):
        if group_id < 0:
            logger.error("Miss group id")
            return
        logger.info(f"Start process group {group_id}")
        # group_dto, status = self.lms_service.get_group(group_id)
        group_response = self._lms_session.get(f"{self._api_root}/sync/statistics/group/{group_id}")
        if group_response.status_code != 200:
            logger.error(f"Group is not found. Response status:{group_response.status_code}")
            return

        students_response = self._lms_session.get(f"{self._api_root}/sync/statistics/students/group/{group_id}")
        if students_response.status_code != 200:
            logger.error(f"Student request failed {students_response.status_code}")
            return

        group_data = group_response.json()
        business = group_data.get("direction").lower()
        location_name = group_data.get("venue").get("name")
        course_id = group_data.get("course").get("key")
        territorial_manager = None
        regional_manager = None
        tutor = None
        if location_name:
            location = Location.objects.filter(lms_location_name=location_name).first()
            if location:
                territorial_manager = location.territorial_manager
                regional_manager = location.regional_manager
                tutor = location.tutor
            else:
                logger.error(f"Location {location_name} not found in DB")
                self.add_fail_group(error_type="location not found",
                                    msg=f"Локація {location_name} не знайдена у базі даних. Група {group_id} ({title})",
                                    regional_manager=regional_manager)
        else:
            logger.error("Location name not specified")
            self.add_fail_group(error_type="location name not specified",
                                msg=f"Локація {location_name} не знайдена у даних від БО. Група {group_id} ({title})",
                                regional_manager=regional_manager)

        students = students_response.json()
        for student in students:
            student_id = student.get("id")
            lessons_response = self._lms_session.get(f"{self._api_root}/sync/statistics/lessons/group/{group_id}")
            attended = False
            if lessons_response.status_code != 200:
                logger.error(f"Lesson get error: {lessons_response.status_code}")
            lesson = lessons_response.json()[0] if len(lessons_response.json()) > 0 else None
            if lesson:
                attended_students = lesson.get("attendedStudent", list())
                attended = student_id in attended_students
            mk_dto = MasterClassDTO(
                student_lms_id=student_id,
                student_lms_name="Placeholder",
                mc_lms_id=group_id,
                start_date=self.start_date,
                end_date=self.end_date,
                business=business,
                location=location_name,
                teacher="Placeholder",
                teacher_lms_id=0,
                tutor=tutor,
                client_manager="Placeholder",
                territorial_manager=territorial_manager,
                regional_manager=regional_manager,
                course_title="Placeholder",
                course_id=course_id,
                attended=attended,
                is_uk=False,
                new_lms=True
            )
            mk_obj, created = self.mk_repository.get_or_create(mk_dto)
            logger.info(f"SUCCESS: Student in {group_id} processed {created}")
        logger.info(f"SUCCESS: Group {group_id} processed")


if __name__ == "__main__":
    statistic_service = MasterClassService(lms_service=LMSService, mk_repository=MasterClassRepository)
    statistic_service.collect_master_classes("2024-10-01", "2024-10-06")
