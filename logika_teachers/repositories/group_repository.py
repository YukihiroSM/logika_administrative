from abc import ABC, abstractmethod
from dataclasses import asdict
from typing import Union, Optional

from logika_statistics.models import Group
from logika_teachers.repositories.dtos import GroupDTO


class GroupRepositoryInterface(ABC):

    @classmethod
    def get_group(cls, group_lms_id: Union[int, str]) -> Optional[GroupDTO]:
        pass

    @classmethod
    def create_group(cls, group_dto: GroupDTO):
        pass


class GroupRepository(GroupRepositoryInterface):

    @classmethod
    def get_group(cls, group_lms_id: Union[int, str]) -> Optional[GroupDTO]:
        group = Group.objects.filter(lms_id=group_lms_id)
        if group:
            return cls._map_object_to_dto(group.first())
        return None

    @classmethod
    def create_group(cls, group_dto: GroupDTO):
        Group.objects.create(**asdict(group_dto))

    @classmethod
    def _map_object_to_dto(cls, obj: Group) -> GroupDTO:
        return GroupDTO(
            lms_id=obj.lms_id,
            title=obj.title,
            status=obj.status,
            type=obj.type,
            venue=obj.venue,
            teacher_name=obj.teacher_name,
            start_date=obj.start_date,
            approximate_end_date=obj.approximate_end_date,
            course_id=obj.course_id,
            teacher_id=obj.teacher_id,
            office_id=obj.office.pk
        )
