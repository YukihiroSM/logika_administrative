from abc import ABC, abstractmethod
from logika_statistics.models import Group
from logika_teachers.repositories.dtos import GroupDTO
from dataclasses import asdict
from typing import Optional


class GroupACLInterface(ABC):

    @classmethod
    @abstractmethod
    def map_dto_to_group(cls, group_dto: GroupDTO) -> Group:
        pass


class GroupACL(GroupACLInterface):
    @classmethod
    def map_dto_to_group(cls, group_dto: GroupDTO) -> Optional[Group]:
        group = Group.objects.filter(**asdict(group_dto))
        if group:
            return group.first()
        return None
