from typing import Union, Optional

from logika_statistics.models import Group
from logika_teachers.services.lms_service import LMSService
from dataclasses import dataclass, asdict
from datetime import date
from abc import ABC, abstractmethod


@dataclass
class GroupDTO:
    lms_id: int
    title: str
    status: str
    type: str
    venue: Optional[str]
    teacher_name: Optional[str]
    start_date: Optional[date]
    approximate_end_date: Optional[date]
    course_id: Optional[int]
    teacher_id: Optional[int]


class GroupServiceInterface(ABC):

    @abstractmethod
    def get_or_create_group(self, group_id: Union[int, str]) -> tuple[Optional[Group], bool]:
        pass


class GroupService(GroupServiceInterface):
    def get_or_create_group(self, group_id: Union[int, str]) -> tuple[Optional[Group], bool]:
        group_qs = Group.objects.filter(lms_id=group_id)
        if group_qs.exitsts():
            return group_qs.first(), False
        else:
            data = self._get_group_data_by_id(group_id=group_id)
            if data:
                group_dto = self._parse_data_to_dto(data=data)
                return Group.objects.create(**asdict(group_dto)), True
            return None, False

    def _parse_data_to_dto(self, data: dict) -> GroupDTO:
        lms_id = data.get("id")
        title = data.get("title")
        status = data.get("status", dict()).get("value")
        venue = data.get("venue", dict()).get("title", "not_set")
        group_type = data.get("type", dict()).get("value")
        teacher_name = data.get("teacher", dict()).get("name")
        start_date = None
        approximate_end_date = None
        course_id = None
        teacher_id = data.get("teacher", dict()).get("id")
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
            teacher_id=teacher_id
        )

    def _get_group_data_by_id(self, group_id: Union[int, str]) -> Optional[dict]:
        data, status = LMSService.get_group(group_id=group_id)
        if status == 200:
            return data
