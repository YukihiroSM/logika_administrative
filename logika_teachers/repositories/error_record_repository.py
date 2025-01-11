from datetime import datetime
from abc import ABC, abstractmethod
from dataclasses import asdict
from typing import Optional, Tuple

from django.db.models import Count

from logika_statistics.models import FailRecord
from logika_teachers.repositories.dtos import FailRecordDTO


class FailRecordRepositoryInterface(ABC):

    @classmethod
    @abstractmethod
    def get_errors_by_type(cls, error_type: str, **additional_filters) -> list[FailRecordDTO]:
        pass

    @classmethod
    @abstractmethod
    def create_error_record(cls, error_dto: FailRecordDTO):
        pass


class FailRecordRepository(FailRecordRepositoryInterface):

    @classmethod
    def get_errors_by_type(cls, error_type: str, **additional_filters) -> list[FailRecordDTO]:
        errors = FailRecord.objects.filter(error_type=error_type)
        if errors.exists():
            errors_list = list()
            for error in errors:
                error_filters = error.additional_filters
                if not additional_filters or all(
                        key in error_filters and error_filters[key] == value
                        for key, value in additional_filters.items()
                ):
                    errors_list.append(cls._map_object_to_dto(error))
            return errors_list
        return list()

    @classmethod
    def _map_object_to_dto(cls, error: FailRecord) -> FailRecordDTO:
        return FailRecordDTO(error_type=error.error_type,
                             error_msg=error.error_msg,
                             additional_filters=error.additional_filters,
                             created_at=error.created_at)

    @classmethod
    def create_error_record(cls, error_dto: FailRecordDTO):
        FailRecord.objects.get_or_create(**asdict(error_dto))

