from dataclasses import asdict

from django.db import IntegrityError
from django.db.models import QuerySet

from logika_teachers.models import PredictedChurn, TeacherComment, TeacherProfile
from logika_teachers.repositories.dtos import ChurnRawDTO, ChurnDTO
from abc import ABC, abstractmethod
from typing import Optional


class ChurnRepositoryInterface(ABC):

    @classmethod
    @abstractmethod
    def create_or_update_churn(cls, churn_dto: ChurnRawDTO) -> ChurnDTO:
        pass

    @classmethod
    @abstractmethod
    def get_churn(cls, churn_id: int, tutor_id: Optional[int] = None) -> Optional[ChurnDTO]:
        pass

    @classmethod
    @abstractmethod
    def get_churns_by_teachers(cls, teachers: list[int], tutor_id: Optional[int] = None) -> list[ChurnDTO]:
        pass


class ChurnRepository(ChurnRepositoryInterface):

    @classmethod
    def create_or_update_churn(cls, churn_dto: ChurnRawDTO) -> ChurnDTO:
        try:
            churn = PredictedChurn.objects.create(**asdict(churn_dto))
        except IntegrityError:
            churn_set = PredictedChurn.objects.filter(
                churn_id=churn_dto.churn_id,
                teacher_id=churn_dto.teacher_id
            )
            churn_set.update(**asdict(churn_dto))
            churn = churn_set.first()

        return cls._map_obj_to_dto(churn)

    @classmethod
    def get_churn(cls, churn_id: int, tutor_id: Optional[int] = None) -> Optional[ChurnDTO]:
        if not tutor_id:
            churn = PredictedChurn.objects.filter(churn_id=churn_id)
        else:
            churn = PredictedChurn.objects.filter(churn_id=churn_id, tutor_id=tutor_id)
        if churn.exists():
            return cls._map_obj_to_dto(churn.first())

    @classmethod
    def get_churns_by_teachers(cls, teachers: list[int], tutor_id: Optional[int] = None) -> list[ChurnDTO]:
        if not tutor_id:
            churns = PredictedChurn.objects.filter(teacher_id__in=teachers)
        else:
            churns = PredictedChurn.objects.filter(teacher_id__in=teachers, tutor_id=tutor_id)
        churn_list = list()
        for churn in churns:
            churn_list.append(cls._map_obj_to_dto(churn))
        return churn_list

    @classmethod
    def _map_obj_to_dto(cls, churn: PredictedChurn) -> ChurnDTO:
        churn_comments = TeacherComment.objects.filter(churn_id=churn.churn_id).order_by("-created_at")
        comment_list = list()
        for comment in churn_comments:
            c = {"description": comment.comment,
                 "created_at": comment.created_at}
            comment_list.append(c)

        churn_dto = ChurnDTO(
            teacher_pk=churn.teacher.pk,
            churn_pk=churn.pk,
            churn_id=churn.churn_id,
            fullname=churn.fullname,
            group_title=churn.group.title if churn.group else "Без групи",
            group_lms=churn.group.lms_id if churn.group else "",
            description=churn.description,
            created_at=churn.created_at,
            comment=churn.comment.comment if churn.comment else "",
            feedback=churn.feedback.id if churn.feedback else None,
            teacher_name=str(churn.teacher),
            teacher_id=churn.teacher.id,
            status=churn.get_status_display(),
            real_status=churn.status,
            STATUS_CHOICES=churn.STATUS_CHOICES,
            priority=churn.priority,
            comments=comment_list
        )
        return churn_dto
