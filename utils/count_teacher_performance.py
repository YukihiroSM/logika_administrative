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
    groups = Group.objects.filter(
        venue__in=locations,
        teacher_id=teacher.lms_id,
        type__in=["regular", "individual"],
    )
    session = get_authenticated_session()
    results = {}
    for group in groups:
        month_performance = []
        group_performance_resp = session.get(
            f"https://lms.logikaschool.com/api/v2/group/lesson/index?groupId={group.lms_id}&status=active&expand=module&perPage=500"
        )
        if group_performance_resp.status_code == 200:
            group_performance_data = group_performance_resp.json()["data"]["items"]
            for lesson in group_performance_data:
                if (
                    "підготовка до ву" in lesson.get("title", "").lower()
                    or "відкритий урок" in lesson.get("title", "").lower()
                    or "revision" in lesson.get("title", "").lower()
                    or "repetition" in lesson.get("title", "").lower()
                ):
                    continue
                if lesson.get("startTime") and is_lesson_in_month(
                    lesson.get("startTime"), month
                ):
                    month_performance.append(
                        lesson.get("regularTaskScoreSumPercent")
                        if lesson.get("regularTaskScoreSumPercent")
                        else 0
                    )
        results[group.lms_id] = month_performance
    return results


def get_resulting_teacher_performance(teacher_id, locations, month):
    month_dict = {
        "Січень": 1,
        "Лютий": 2,
        "Березень": 3,
        "Квітень": 4,
        "Травень": 5,
        "Червень": 6,
        "Липень": 7,
        "Серпень": 8,
        "Вересень": 9,
        "Жовтень": 10,
        "Листопад": 11,
        "Грудень": 12,
    }
    if month and locations:
        result = get_teacher_performance_by_month(
            teacher_id, locations, month_dict[month]
        )
        groups_data = {}

        if result:
            session = get_authenticated_session()
            groups_data["teacher_average"] = 0
            group_count = 0
            for group in result:
                if len(result[group]) < 1:
                    continue
                group_count += 1
                group_resp = session.get(
                    f"https://lms.logikaschool.com/api/v1/group/{group}"
                )
                group_data = group_resp.json()["data"]
                group_title = group_data["title"].replace("_", "")
                groups_data[group] = {}
                groups_data[group]["average"] = (
                    sum(result[group]) / len(result[group]) if result[group] else 0
                )
                groups_data[group]["max"] = max(result[group]) if result[group] else 0
                groups_data[group]["min"] = min(result[group]) if result[group] else 0
                groups_data[group]["title"] = group_title
                groups_data["teacher_average"] += groups_data[group]["average"]
            groups_data["teacher_average"] = (
                groups_data["teacher_average"] / group_count
            )
            return groups_data
