from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional, Union


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
    office_id: int


@dataclass
class StudentDTO:
    first_name: str
    last_name: str
    group_id: Optional[int]


@dataclass
class LessonRawDTO:
    lesson_id: int
    lesson_title: str
    start_time_formatted: str
    status: str


@dataclass
class LessonDTO:
    lesson_id: int
    lesson_title: str
    start_time_formatted: str
    status: str
    group_name: str
    group_id: int
    teacher: str
    teacher_id: int
    last_comment: Optional[str]


@dataclass
class ChurnRawDTO:
    churn_id: str
    status: str
    teacher_id: int
    description: str = ""
    feedback_id: Optional[int] = None


@dataclass
class ChurnDTO:
    teacher_pk: int
    churn_pk: int
    churn_id: Union[int, str]
    fullname: str
    description: str
    created_at: date
    feedback: Optional[int]
    teacher_name: str
    teacher_id: int
    status: str
    real_status: str
    STATUS_CHOICES: tuple
    priority: int
    comments: list[dict]
    comment: str = ""
    group_lms: Union[int, str] = ""
    group_title: str = "Без групи"
