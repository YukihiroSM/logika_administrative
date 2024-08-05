from datetime import datetime
from typing import Type, Union

from logika_teachers.services.lms_service import LMSServiceInterface


class LessonFacade:
    def __init__(self, lms_service: Type[LMSServiceInterface], group_id: Union[str, int]):
        self.lms_service = lms_service
        self.lessons = self._get_lessons(group_id)

    def _get_lessons(self, group_id: Union[str, int]) -> list:
        data, status = self.lms_service.get_lessons(group_id)
        if status == 200:
            return data
        return list()

    def filter_open_lessons(self):
        self.lessons = [lesson for lesson in self.lessons if "Відкритий" in lesson["lesson_title"]]

    def filter_lessons_by_date(self, from_date: datetime, to_date: datetime):
        future_lessons = []

        for les in self.lessons:
            date_str = les.get("start_time_formatted")[3:]
            date_obj = datetime.strptime(date_str, "%d.%m.%y %H:%M")

            if from_date <= date_obj <= to_date:
                future_lessons.append(les)

        self.lessons = future_lessons


