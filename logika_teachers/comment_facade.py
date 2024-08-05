from abc import ABC, abstractmethod

from django.db.models import QuerySet

from logika_teachers.services.lms_service import LMSService
from logika_teachers.models import TeacherComment, TeacherProfile, TutorProfile


class CommentsFacadeInterface(ABC):

    def __init__(self, teacher: TeacherProfile, tutor: TutorProfile):
        self.teacher = teacher
        self.tutor = tutor

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
            data, status = LMSService.get_group(comm.group_id)
            if status == 200:
                comm.group_title = data.get('title')
            else:
                comm.group_title = "Not found " + str(comm.group_id)
        return comments

    def get_all_comments(self) -> QuerySet[TeacherComment]:
        comments = TeacherComment.objects.filter(teacher=self.teacher, tutor=self.tutor).order_by("-created_at")
        for comm in comments:
            if comm.comment_type == "lesson":
                data, status = LMSService.get_group(comm.group_id)
                if status == 200:
                    comm.group_title = data.get('title')
                else:
                    comm.group_title = "Not found" + str(comm.group_id)
            elif comm.comment_type == "predicted_churn":
                data, status = LMSService.get_student(comm.churn_id)
                if status == 200:
                    comm.churn_name = data.get("last_name") + " " + data.get("first_name")
                else:
                    comm.churn_name = "Not found" + str(comm.churn_id)
        return comments
