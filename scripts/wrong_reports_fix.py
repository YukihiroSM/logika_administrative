from logika_statistics.models import StudentReport, Location
from utils.lms_authentication import get_authenticated_session


def run():
    wrong_reports = StudentReport.objects.filter(
        payment=1,
        territorial_manager__isnull=True,
        start_date__in=("2024-02-01", "2024-02-05", "2024-02-12", "2024-02-19"),
        business="programming",
    ).all()

    session = get_authenticated_session()
    for report in wrong_reports:
        student_id = report.student_lms_id
        student_details_url = f"https://lms.logikaschool.com/api/v2/student/default/view/{student_id}?id={student_id}&expand=lastGroup%2Cwallet%2Cbranch%2ClastGroup.branch%2CamoLead%2Cgroups%2Cgroups.b2bPartners"
        student_details_resp = session.get(student_details_url)
        if student_details_resp.status_code == 200:
            student_groups = student_details_resp.json()["data"]["groups"][::-1]
            for group in student_groups:
                if "МК" in group["title"]:
                    group_details_resp = session.get(
                        f"https://lms.logikaschool.com/api/v1/group/{group['id']}?expand=venue%2Cteacher%2Ccurator%2Cbranch"
                    )
                    if group_details_resp.status_code == 200:
                        group_data = group_details_resp.json()["data"]

                        try:
                            location = group_data["venue"].get("title")
                        except:
                            continue
                        client_manager = None
                        if group_data["curator"] and group_data["curator"]["name"]:
                            client_manager = group_data["curator"]["name"]
                        location_obj = Location.objects.filter(
                            lms_location_name=location
                        ).first()
                        if location_obj:
                            report.location = location
                            report.client_manager = (
                                client_manager
                                if client_manager
                                else location_obj.client_manager
                            )
                            report.territorial_manager = (
                                location_obj.territorial_manager
                            )
                            report.regional_manager = location_obj.regional_manager
                            report.save()
                            break
            group = student_groups[0]
            group_details_resp = session.get(
                f"https://lms.logikaschool.com/api/v1/group/{group['id']}?expand=venue%2Cteacher%2Ccurator%2Cbranch"
            )
            if group_details_resp.status_code == 200:
                group_data = group_details_resp.json()["data"]
                location = group_data["venue"]
                if location:
                    location = group_data["venue"].get("title")
                else:
                    location = None
                teacher = group_data.get("teacher")
                if teacher:
                    teacher = group_data["teacher"].get("id")
                    report.teacher = teacher
                    report.save()

                client_manager = group_data.get("curator")
                if client_manager:
                    client_manager = group_data["curator"].get("name")
                location_obj = Location.objects.filter(
                    lms_location_name=location
                ).first()
                if location_obj:
                    report.location = location
                    report.client_manager = (
                        client_manager
                        if client_manager
                        else location_obj.client_manager
                    )
                    report.territorial_manager = location_obj.territorial_manager
                    report.regional_manager = location_obj.regional_manager
                    report.save()
                else:
                    report.location = location
                    report.save()
