from django.db.models import QuerySet

from logika_statistics.models import Group
from logika_teachers.models import TeacherProfile
from typing import Union


def get_teacher_group_titles(teacher_id) -> QuerySet[str]:
    teacher = TeacherProfile.objects.get(id=teacher_id)
    groups = Group.objects.filter(
            teacher_id=teacher.lms_id,
            type__in=("regular", "individual", "Группа", "Индивидуальная"),
        )
    return groups.values_list("title", flat=True).distinct()


def get_teacher_groups(teacher_id) -> QuerySet[Group]:
    teacher = TeacherProfile.objects.get(id=teacher_id)
    groups = Group.objects.filter(
            teacher_id=teacher.lms_id,
            type__in=("regular", "individual", "Группа", "Индивидуальная"),
        )
    return groups.distinct()
