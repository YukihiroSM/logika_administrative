import logging
from logika_statistics.models import Group
from logika_teachers.models import PredictedChurn, TeacherComment
from logika_teachers.repositories.churn_repository import ChurnRepository
from logika_teachers.repositories.dtos import ChurnRawDTO
import time


def run():
    comments = TeacherComment.objects.filter(churn_id__isnull=False)
    total = 0
    for comment in comments:
        churn_id = comment.churn_id
        teacher_id = comment.teacher.pk
        tutor_id = comment.tutor.pk
        churn = PredictedChurn.objects.filter(churn_id=churn_id, teacher_id=teacher_id).first()
        if churn:
            churn.tutor_id = tutor_id
            churn.save()
            total += 1
            print(f"{churn.churn_id} updated")
        else:
            print(churn_id, "error")

        
    print(total)

