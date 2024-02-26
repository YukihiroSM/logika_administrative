from django.core.management.base import BaseCommand, CommandError
from utils.lms_authentication import get_authenticated_session
from logika_statistics.models import Group
from utils.constants import GROUP_STATUSES, GROUP_TYPES


class Command(BaseCommand):
    help = "Closes the specified poll for voting"

    # def add_arguments(self, parser):
    #     parser.add_argument("poll_ids", nargs="+", type=int)

    def handle(self, *args, **options):
        session = get_authenticated_session()
        groups_resp = session.get("https://lms.logikaschool.com/api/v1/group")

        if groups_resp.status_code == 200:
            groups_data = groups_resp.json()["data"]["items"]
            for group in groups_data:
                if (
                    group["status"]["value"] not in GROUP_STATUSES
                    or group["type"]["value"] not in GROUP_TYPES
                ):
                    continue

                teacher_name = group.get("teacherName", "not_set")
                teacher_id = None
                if teacher_name != "not_set":
                    detailed_group_resp = session.get(
                        f"https://lms.logikaschool.com/api/v1/group/{group['id']}?expand=venue%2Cteacher%2Ccurator%2Cbranch"
                    )
                    if detailed_group_resp.status_code == 200:
                        detailed_group_data = detailed_group_resp.json()["data"]
                        if detailed_group_data.get("teacher"):
                            teacher_id = detailed_group_data["teacher"]["id"]
                        else:
                            teacher_id = None
                group_id = group["id"]
                group_name = group["title"]
                group_status = group["status"]["value"]
                group_type = group["type"]["value"]
                group_venue = group.get("venue", "not_set")
                try:
                    group_obj, created = Group.objects.get_or_create(
                        lms_id=group_id,
                        title=group_name,
                        status=group_status,
                        type=group_type,
                        venue=group_venue,
                        teacher_name=teacher_name,
                        teacher_id=teacher_id,
                    )
                except:
                    self.stdout.write(self.style.ERROR(f"Group {group_name} duplicated"))
                group_obj.save()
                if created:
                    self.stdout.write(self.style.SUCCESS(f"Group {group_name} created"))
                else:
                    group_obj.title = group_name
                    group_obj.status = group_status
                    group_obj.type = group_type
                    group_obj.venue = group_venue
                    group_obj.teacher_name = teacher_name
                    group_obj.teacher_id = teacher_id
                    group_obj.save()
                    self.stdout.write(
                        self.style.WARNING(
                            f"Group {group_name} already exists. Updated data."
                        )
                    )

        else:
            print(groups_resp.status_code)
            print(groups_resp.content)
