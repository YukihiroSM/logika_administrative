import logging
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor

import requests

import library
from logika_statistics.models import MasterClassRecord, PaymentRecord, Location
from utils.lms_authentication import get_authenticated_session

logger = logging.getLogger("info_logger")


class PaymentServiceInterface(ABC):

    def __init__(self, course: str = "programming"):
        self.start_date = None
        self.end_date = None
        self.course = course
        self.failed_payments = {"too small": list(),
                                "location not found": list(),
                                "other": list(),
                                "wrong id": list(),
                                "without mk": list()}

    @abstractmethod
    def collect_payments(self, start_date: str, end_date: str):
        pass


class PaymentService(PaymentServiceInterface):
    _payments_url = "https://localhost:22443/SCHOOL/ru_RU/hs/1cData/B2C/?from={0}&till={1}&businessDirection={2}&firstPayment=true"
    _student_url = "https://lms.logikaschool.com/api/v2/student/default/view/{0}?id={0}&expand=lastGroup%2Cwallet%2Cbranch%2ClastGroup.branch%2CamoLead%2Cgroups%2Cgroups.b2bPartners"
    _group_url = "https://lms.logikaschool.com/api/v1/group/{0}?expand=venue,teacher,curator"
    _lms_session = get_authenticated_session()

    def __init__(self, course: str = "programming"):
        super().__init__(course=course)
        self._convent_course_to_url()

    def collect_payments(self, start_date: str, end_date: str):
        self.start_date = start_date
        self.end_date = end_date
        self._convert_date_to_url()
        url = self._payments_url.format(self.start_date, self.end_date, self.course)
        session = self._get_session()
        data = self._get_payments_data(url, session)
        if data:
            self._process_data_in_threads(data)

    def _convert_date_to_url(self):
        self.start_date = self.start_date.replace("-", "")
        self.end_date = self.end_date.replace("-", "")

    def _convent_course_to_url(self):
        self.course = (
            "Школы Программирования"
            if self.course == "programming"
            else "english"
        )

    def _get_session(self):
        session = requests.Session()
        session.headers = library.payments_headers
        session.verify = False
        return session

    def _get_payments_data(self, url: str, session: requests.Session):
        logger.info(f"Request url: {url}")
        response = session.get(url)
        if not response.ok:
            logger.error(f"One C Http error: {response.status_code}")
            return

        return response.json()

    def _process_data_in_threads(self, data: list, max_threads=6):
        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            futures = [executor.submit(self._process_payment, row) for row in data]

    def _get_true_payment_value(self, value):
        if value is None:
            return 0
        if isinstance(value, str):
            value = value.replace(".00", "").replace(",", "")
            return int(value)
        else:
            return value

    def _process_payment(self, payment):
        student_id = payment["КлиентID_БО"]
        business = (
            "programming"
            if payment["НаправлениеБизнеса"] == "Школы программирования"
            else "english"
        )
        if self._get_true_payment_value(payment["Оплата"]) < 500:
            logger.warning(f"too small payment {str(payment['КлиентID_БО'])}")
            self.failed_payments["too small"].append(student_id)
            return

        existing_report = (
            MasterClassRecord.objects.filter(
                student_lms_id=student_id, business=business, attended=True
            )
            .order_by("-start_date")
            .first()
        )
        if existing_report:
            report = PaymentRecord.objects.get_or_create(
                student_lms_id=existing_report.student_lms_id,
                student_lms_name=existing_report.student_lms_name,
                recent_group_lms_id=existing_report.mc_lms_id,
                start_date=self.start_date,
                end_date=self.end_date,
                business=business,
                location=existing_report.location,
                teacher=existing_report.teacher,
                teacher_lms_id=existing_report.teacher_lms_id,
                client_manager=existing_report.client_manager,
                territorial_manager=existing_report.territorial_manager,
                regional_manager=existing_report.regional_manager,
                course_title=existing_report.course_title,
                course_id=existing_report.course_id,
                payment_amount=self._get_true_payment_value(payment["Оплата"]),
            )
            return
        student_url = self._student_url.format(student_id)
        student_details_response = self._lms_session.get(student_url)
        if student_details_response.status_code == 404:
            logger.warning(f"student {student_id} not found in LMS")
            self.failed_payments["wrong id"].append(student_id)
            return

        try:
            student_details = student_details_response.json()["data"]
        except KeyError:
            logger.warning(f"Can't get data about student {student_id} Skipping!")
            self.failed_payments["other"].append(student_id)
            return

        student_lms_name = student_details.get("fullName")
        student_lms_id = student_details.get("id")
        student_recent_group = student_details.get("lastGroup")

        if student_recent_group is None:
            logger.warning(f"student {student_id} has no recent group")
            self.failed_payments["without mk"].append(student_id)
            return

        student_recent_group_id = student_recent_group.get("id")
        group_url = self._group_url.format(student_recent_group_id)
        group_response = self._lms_session.get(group_url)

        if group_response.status_code != 200:
            logger.warning(
                f"group {student_recent_group_id} unable to retrieve from LMS"
            )
            self.failed_payments["other"].append(student_id)
            return
        group_data = group_response.json()["data"]
        group_teacher_data = group_data.get("teacher")
        group_venue_data = group_data.get("venue")
        group_curator_data = group_data.get("curator")
        group_course_data = group_data.get("course")

        if group_teacher_data is None:
            logger.warning(f"group {student_recent_group_id} has no teacher")

        if group_venue_data is None:
            logger.warning(f"group {student_recent_group_id} has no venue")

        if group_curator_data is None:
            logger.warning(f"group {student_recent_group_id} has no curator")

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
            logger.warning(
                f"student {student_id} has wrong business {course_business}"
            )

        location_object = Location.objects.filter(
            lms_location_name=location
        ).first()
        if location_object is None:
            logger.warning(f"location {location} not found in DB")
            self.failed_payments["location not found"].append(student_id)

        territorial_manager = None
        regional_manager = None

        if location_object:
            territorial_manager = location_object.territorial_manager
            regional_manager = location_object.regional_manager

        report = PaymentRecord.objects.get_or_create(
            student_lms_id=student_lms_id,
            student_lms_name=student_lms_name,
            recent_group_lms_id=student_recent_group_id,
            start_date=self.start_date,
            end_date=self.end_date,
            business=business,
            location=location,
            teacher=teacher,
            teacher_lms_id=teacher_lms_id,
            client_manager=client_manager,
            territorial_manager=territorial_manager,
            regional_manager=regional_manager,
            course_title=course_title,
            course_id=course_id,
            payment_amount=self._get_true_payment_value(payment["Оплата"]),
        )
