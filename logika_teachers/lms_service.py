from abc import ABC, abstractmethod
from typing import Any, Optional, Union

from requests import Response

from utils.lms_authentication import get_authenticated_session


class LMSServiceInterface(ABC):

    @classmethod
    @abstractmethod
    def get_student(cls, student_id: Union[str, int]) -> tuple[Optional[dict], int]:
        pass

    @classmethod
    @abstractmethod
    def get_group(cls, group_id: Union[str, int]) -> tuple[Optional[dict], int]:
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
    def get_student(cls, student_id: Union[str, int]) -> tuple[Optional[dict], int]:
        response = cls._session.get(url=cls._student_url.format(student_id))
        return cls._validate_response(response)

    @classmethod
    def get_group(cls, group_id: Union[str, int]) -> tuple[Optional[dict], int]:
        response = cls._session.get(url=cls._group_url.format(group_id))
        return cls._validate_response(response)

    @classmethod
    def get_lessons(cls, group_id: Union[str, int]) -> tuple[Optional[list], int]:
        response = cls._session.get(url=cls._lessons_url.format(group_id))
        data, status = cls._validate_response(response)
        if status == 200:
            data = data[0].get("attendance")
        return data, status

    @classmethod
    def _validate_response(cls, response: Response) -> tuple[Any, int]:
        if response.status_code == 200:
            return response.json().get("data"), response.status_code
        else:
            return None, response.status_code
