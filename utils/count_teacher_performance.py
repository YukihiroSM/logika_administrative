from logika_statistics.models import Group
from logika_teachers.models import TeacherProfile
from datetime import datetime
from utils.lms_authentication import get_authenticated_session


def is_lesson_in_month(lesson_date, month):
    # lesson_date_example: 2023-03-13T20:30:00+03:00
    lesson_date = datetime.strptime(lesson_date, "%Y-%m-%dT%H:%M:%S%z")
    if lesson_date.month == month:
        return True


def get_teacher_performance_by_month(teacher_id, locations, month):
    teacher = TeacherProfile.objects.get(id=teacher_id)
    groups = Group.objects.filter(venue__in=locations, teacher_id=teacher.lms_id)
    session = get_authenticated_session()
    results = {}
    for group in groups:
        month_performance = []
        if group.type == "regular":
            group_performance_resp = session.get(
                f"https://lms.logikaschool.com/api/v2/group/lesson/index?groupId={group.lms_id}&status=active&expand=module&perPage=500"
            )
            if group_performance_resp.status_code == 200:
                group_performance_data = group_performance_resp.json()["data"]["items"]
                for lesson in group_performance_data:
                    if lesson.get("startTime") and is_lesson_in_month(lesson.get("startTime"), month):
                        month_performance.append(
                            lesson.get("regularTaskScoreSumPercent") if lesson.get("regularTaskScoreSumPercent") else 0
                        )
        results[group.lms_id] = month_performance
    return results
