from abc import ABC, abstractmethod
from typing import Type

from django.db.models import QuerySet

from logika_teachers.services.lms_service import LMSServiceInterface
from logika_teachers.models import TeacherComment, TeacherProfile, TutorProfile


class CommentsFacadeInterface(ABC):

    def __init__(self, teacher: TeacherProfile, tutor: TutorProfile, lms_service: Type[LMSServiceInterface]):
        self.teacher = teacher
        self.tutor = tutor
        self.lms_service = lms_service

    @abstractmethod
    def get_call_comments(self) -> QuerySet[TeacherComment]:
        pass

    @abstractmethod
    def get_lesson_comments(self) -> QuerySet[TeacherComment]:
        pass

    @abstractmethod
    def get_all_comments(self) -> QuerySet[TeacherComment]:
        pass


class CommentsFacade(CommentsFacadeInterface):

    def get_call_comments(self) -> QuerySet[TeacherComment]:
        comments = TeacherComment.objects.filter(teacher=self.teacher, tutor=self.tutor, comment_type="call")
        return comments.order_by("-created_at")

    def get_lesson_comments(self) -> QuerySet[TeacherComment]:
        comments = TeacherComment.objects.filter(teacher=self.teacher, tutor=self.tutor, comment_type="lesson")
        comments = comments.order_by("-created_at")
        for comm in comments:
            group_dto, status = self.lms_service.get_group(comm.group_id.strip())
            if status == 200:
                comm.group_title = group_dto.title
            else:
                comm.group_title = "Not found " + str(comm.group_id)
        return comments

    def get_all_comments(self) -> QuerySet[TeacherComment]:
        comments = TeacherComment.objects.filter(teacher=self.teacher, tutor=self.tutor).order_by("-created_at")
        for comm in comments:
            if comm.comment_type == "lesson":
                group_dto, status = self.lms_service.get_group(comm.group_id.strip())
                if status == 200:
                    comm.group_title = group_dto.title
                else:
                    comm.group_title = "Not found " + str(comm.group_id)
            elif comm.comment_type == "predicted_churn":
                student_dto, status = self.lms_service.get_student(comm.churn_id)
                if status == 200:
                    comm.churn_name = student_dto.last_name + " " + student_dto.first_name
                else:
                    comm.churn_name = "Not found " + str(comm.churn_id)
        return comments
