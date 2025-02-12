from datetime import datetime
from abc import ABC, abstractmethod
from dataclasses import asdict
from typing import Optional, Tuple

from django.db.models import Count

from logika_statistics.models import MasterClassRecord
from logika_teachers.repositories.dtos import MasterClassDTO


class MasterClassRepositoryInterface(ABC):

    @classmethod
    @abstractmethod
    def get_or_create(cls, mk_dto: MasterClassDTO) -> tuple[MasterClassRecord, bool]:
        pass

    @classmethod
    @abstractmethod
    def get_master_class_statistics(cls, start_date: datetime, **extra_filters) -> list:
        pass

    @classmethod
    @abstractmethod
    def get_student_lms_ids(cls, start_date: datetime, **extra_filters) -> list:
        pass
    

class MasterClassRepository(MasterClassRepositoryInterface):

    @classmethod
    def get_or_create(cls, mk_dto: MasterClassDTO) -> tuple[MasterClassRecord, bool]:
        mk, created = MasterClassRecord.objects.get_or_create(**asdict(mk_dto))
        return mk, created

    @classmethod
    def get_master_class_statistics(cls, start_date: datetime, **extra_filters) -> list:
        master_classes_count = MasterClassRecord.objects.filter(start_date=start_date,
                                                                **extra_filters) \
            .values('regional_manager', 'territorial_manager', 'location', 'attended') \
            .annotate(count=Count('id'))

        return list(master_classes_count)

    @classmethod
    def get_student_lms_ids(cls, start_date: datetime, **extra_filters) -> list:
        student_ids = MasterClassRecord.objects.filter(start_date=start_date, **extra_filters).\
            values_list("student_lms_id", flat=True)
        return list(student_ids)
