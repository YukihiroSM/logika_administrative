from datetime import datetime
from typing import Union, Optional, Type

from logika_teachers.models import TeacherProfile
from logika_teachers.repositories.dtos import LessonRawDTO, LessonDTO
from logika_teachers.services.lms_service import LMSServiceInterface
from logika_teachers.services.group_service import GroupServiceInterface
from abc import ABC, abstractmethod


class LessonServiceInterface(ABC):

    def __init__(self, lms_service: Type[LMSServiceInterface], group_service: GroupServiceInterface):
        self.lms_service = lms_service
        self.group_service = group_service

    @abstractmethod
    def get_lessons(self, group_id: int) -> list[LessonDTO]:
        pass

    @abstractmethod
    def filter_open_lessons(self, lessons: list[LessonDTO]) -> list[LessonDTO]:
        pass

    @abstractmethod
    def filter_lessons_by_date(self,
                               lessons: list[LessonDTO],
                               from_date: datetime,
                               to_date: datetime) -> list[LessonDTO]:
        pass


class LessonService(LessonServiceInterface):

    def get_lessons(self, group_id: int) -> list[LessonDTO]:
        raw_lessons, status = self.lms_service.get_lessons(group_id=group_id)
        lessons = self._cook_lessons(raw_lessons, group_id)
        return lessons

    def _cook_lessons(self, raw_lessons: list[LessonRawDTO], group_id: int):
        if raw_lessons is None:
            return list()
        group_dto, created = self.group_service.get_or_create_group(group_id=group_id)
        teacher = TeacherProfile.objects.filter(lms_id=group_dto.teacher_id).first()
        title = "Не знайдено"
        group_id = 0
        teacher_name = "Не знайдено"
        teacher_id = 0
        if group_dto:
            title = group_dto.title
            group_id = group_dto.lms_id
            teacher_name = group_dto.teacher_name
            teacher_id = teacher.id

        cook_lessons = list()
        for les in raw_lessons:
            cook_lessons.append(LessonDTO(
                lesson_id=les.lesson_id,
                lesson_title=les.lesson_title,
                start_time_formatted=les.start_time_formatted,
                status=les.status,
                group_name=title,
                group_id=group_id,
                teacher=teacher_name,
                teacher_id=teacher_id,
                last_comment=None
            ))
        return cook_lessons

    def filter_open_lessons(self, lessons: list[LessonDTO]) -> list[LessonDTO]:
        lessons = [lesson for lesson in lessons
                   if "Відкритий" in lesson.lesson_title
                   or "Open" in lesson.lesson_title
                   or "Реліз" in lesson.lesson_title
                   or "Release" in lesson.lesson_title]
        return lessons

    def filter_lessons_by_date(self, lessons: list[LessonDTO], from_date: datetime, to_date: datetime) -> list[LessonDTO]:
        future_lessons = []

        for les in lessons:
            date_str = les.start_time_formatted[3:]
            date_obj = datetime.strptime(date_str, "%d.%m.%y %H:%M")

            if from_date <= date_obj <= to_date:
                future_lessons.append(les)

        return future_lessons
