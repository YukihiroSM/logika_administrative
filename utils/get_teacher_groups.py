from logika_statistics.models import Group
from logika_teachers.models import TeacherProfile


def get_teacher_groups(teacher_id):
    teacher = TeacherProfile.objects.get(id=teacher_id)
    locations = (
        Group.objects.filter(
            teacher_id=teacher.lms_id, type__in=("regular", "individual")
        )
        .values_list("title", flat=True)
        .distinct()
    )
    return locations
