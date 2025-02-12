from logika_statistics.models import Group
from logika_teachers.models import TeacherProfile
import logging
logger = logging.getLogger("info_logger")

def get_teacher_locations(teacher_id):
    teacher = TeacherProfile.objects.get(id=teacher_id)
    logger.info(f"{teacher.lms_id}")
    locations = (
        Group.objects.filter(teacher_id=teacher.lms_id)
        .values_list("venue", flat=True)
        .distinct()
    )
    return locations
