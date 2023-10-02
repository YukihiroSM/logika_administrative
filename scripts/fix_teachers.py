from logika_statistics.models import Group
from utils.lms_authentication import get_authenticated_session

def run():
    groups = Group.objects.filter(teacher_id=None).exclude(teacher_name=None).all()
    session = get_authenticated_session()
    for group in groups:
        group_link = f"https://lms.logikaschool.com/api/v1/group/{group.lms_id}?expand=venue%2Cteacher%2Ccurator%2Cbranch"
        group_resp = session.get(group_link)
        if group_resp.status_code == 200:
            group_data = group_resp.json()["data"]
            teacher = group_data["teacher"]
            if teacher:
                teacher_id = teacher["id"]
                group.teacher_id = teacher_id
                group.save()
