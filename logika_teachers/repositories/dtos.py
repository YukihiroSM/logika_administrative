from dataclasses import dataclass, field
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
    tutor_id: Optional[int] = None


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


@dataclass
class MasterClassDTO:
    student_lms_id: Union[int, str]
    mc_lms_id: Union[int, str]
    start_date: str
    end_date: str
    business: str
    location: str
    teacher_lms_id: Union[int, str]
    tutor: str
    territorial_manager: str
    regional_manager: str
    course_id: Union[int, str]
    attended: bool
    is_uk: bool = False
    student_lms_name: str = "Placeholder"
    course_title: str = "Placeholder"
    client_manager: str = "Placeholder"
    teacher: str = "Placeholder"
    new_lms: bool = False


@dataclass
class MKReportDTO:
    service_name: str
    mk_data: list
    student_ids: list
    total_mk: int
    location_data: dict = field(default_factory=dict)


@dataclass
class PMReportDTO:
    pm_data: list
    total_pm: int
    location_data: dict = field(default_factory=dict)
