from typing import Union, Optional, Type
from logika_teachers.repositories.dtos import GroupDTO
from logika_teachers.repositories.group_repository import GroupRepositoryInterface
from logika_teachers.services.lms_service import LMSServiceInterface
from abc import ABC, abstractmethod


class GroupServiceInterface(ABC):

    def __init__(self, lms_service: Type[LMSServiceInterface], group_repository: Type[GroupRepositoryInterface]):
        self.lms_service = lms_service
        self.group_repository = group_repository

    @abstractmethod
    def get_or_create_group(self, group_id: Union[int, str]) -> tuple[Optional[GroupDTO], bool]:
        pass


class GroupService(GroupServiceInterface):
    def get_or_create_group(self, group_id: Union[int, str]) -> tuple[Optional[GroupDTO], bool]:
        group_dto = self.group_repository.get_group(group_id)
        if group_dto:
            return group_dto, False
        else:
            group_dto = self._get_group_data_by_id(group_id=group_id)
            if group_dto:
                self.group_repository.create_group(group_dto)
                return group_dto, True
            return None, False

    def _get_group_data_by_id(self, group_id: Union[int, str]) -> Optional[GroupDTO]:
        group_dto, status = self.lms_service.get_group(group_id=group_id)
        if status == 200:
            return group_dto
