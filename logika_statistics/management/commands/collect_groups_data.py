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
                if (group["status"]["value"] not in GROUP_STATUSES
                        or group["type"]["value"] not in GROUP_TYPES):
                    continue

                teacher_name = group.get("teacherName", "not_set")
                group_id = group["id"]
                group_name = group["title"]
                group_status = group["status"]["value"]
                group_type = group["type"]["value"]
                group_venue = group.get("venue", "not_set")
                group_obj, created = Group.objects.get_or_create(
                    lms_id=group_id,
                    title=group_name,
                    status=group_status,
                    type=group_type,
                    venue=group_venue,
                    teacher_name=teacher_name,
                )
                group_obj.save()
                if created:
                    self.stdout.write(self.style.SUCCESS(f"Group {group_name} created"))
                else:
                    group_obj.title = group_name
                    group_obj.status = group_status
                    group_obj.type = group_type
                    group_obj.venue = group_venue
                    group_obj.teacher_name = teacher_name
                    group_obj.save()
                    self.stdout.write(self.style.SUCCESS(f"Group {group_name} already exists. Updated data."))


