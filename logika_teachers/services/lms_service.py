from abc import ABC, abstractmethod
from typing import Any, Optional, Union

from requests import Response

from logika_teachers.repositories.dtos import StudentDTO, GroupDTO, LessonDTO, LessonRawDTO
from utils.lms_authentication import get_authenticated_session
from logika_statistics.models import OfficeRegion


class LMSServiceInterface(ABC):

    @classmethod
    @abstractmethod
    def get_student(cls, student_id: Union[str, int]) -> tuple[Optional[StudentDTO], int]:
        pass

    @classmethod
    @abstractmethod
    def get_group(cls, group_id: Union[str, int]) -> tuple[Optional[GroupDTO], int]:
        pass

    @classmethod
    @abstractmethod
    def get_lessons(cls, group_id: Union[str, int]) -> tuple[Optional[list], int]:
        pass


class LMSService(LMSServiceInterface):
    _student_url = 'https://lms.logikaschool.com/api/v1/student/view/{0}?expand=branch,group'
    _group_url = 'https://lms.logikaschool.com/api/v1/group/{0}?expand=venue%2Cteacher%2Ccurator%2Cbranch'
    _lessons_url = 'https://lms.logikaschool.com/api/v1/stats/default/attendance?group={0}'
    _session = get_authenticated_session()

    @classmethod
    def get_student(cls, student_id: Union[str, int]) -> tuple[Optional[StudentDTO], int]:
        response = cls._session.get(url=cls._student_url.format(student_id))
        data, status = cls._validate_response(response)
        return cls._parse_student(data), status

    @classmethod
    def get_group(cls, group_id: Union[str, int]) -> tuple[Optional[GroupDTO], int]:
        response = cls._session.get(url=cls._group_url.format(group_id))
        data, status = cls._validate_response(response)
        return cls._parse_group(data), status

    @classmethod
    def get_lessons(cls, group_id: Union[str, int]) -> tuple[Optional[list[LessonRawDTO]], int]:
        response = cls._session.get(url=cls._lessons_url.format(group_id))
        data, status = cls._validate_response(response)
        if status == 200:
            if len(data) == 0:
                status = 400
                return data, status
            data = data[0].get("attendance")
            raw_lessons = cls._parse_lessons(data)
            return raw_lessons, status
        return data, status

    @classmethod
    def _validate_response(cls, response: Response) -> tuple[Any, int]:
        if response.status_code == 200:
            return response.json().get("data"), response.status_code
        else:
            return None, response.status_code

    @classmethod
    def _parse_student(cls, data: dict) -> Optional[StudentDTO]:
        if not data:
            return None
        first_name = data["first_name"]
        last_name = data["last_name"]
        group = data["group"]
        group_id = None
        if group:
            group_id = group["id"]
        return StudentDTO(first_name=first_name, last_name=last_name, group_id=group_id)

    @classmethod
    def _parse_group(cls, data: dict) -> Optional[GroupDTO]:
        if not data:
            return None
        lms_id = data.get("id")
        title = data.get("title")
        status = data.get("status").get("value")
        venue = data.get("venue").get("title", "not_set") if data.get("venue") else None
        group_type = data.get("type").get("value")
        teacher_name = data.get("teacher").get("name") if data.get("teacher") else None
        start_date = None
        approximate_end_date = None
        course_id = None
        teacher_id = data.get("teacher").get("id") if data.get("teacher") else None
        office = data.get("branch").get("title") if data.get("branch") else ""
        office_obj, created = OfficeRegion.objects.get_or_create(name=office)

        return GroupDTO(
            lms_id=lms_id,
            title=title,
            status=status,
            type=group_type,
            venue=venue,
            teacher_name=teacher_name,
            start_date=start_date,
            approximate_end_date=approximate_end_date,
            course_id=course_id,
            teacher_id=teacher_id,
            office_id=office_obj.pk
        )

    @classmethod
    def _parse_lessons(cls, data: list) -> Optional[list[LessonRawDTO]]:
        if not data:
            return None
        raw_lessons = list()
        for les in data:
            raw_lessons.append(LessonRawDTO(
                lesson_id=les.get("lesson_id"),
                lesson_title=les.get("lesson_title", ""),
                start_time_formatted=les.get("start_time_formatted", ""),
                status=les.get("status", str)
            ))
        return raw_lessons
