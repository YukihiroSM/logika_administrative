from django.core.management.base import BaseCommand, CommandError
from utils.lms_authentication import get_authenticated_session
from logika_statistics.models import Group
from utils.constants import GROUP_STATUSES_LIST, GROUP_TYPES_LIST
import csv
from django.conf import settings

GROUPS_FILE_PATH = settings.BASE_DIR / "groups_data.csv"


class Command(BaseCommand):
    help = "Closes the specified poll for voting"

    # def add_arguments(self, parser):
    #     parser.add_argument("poll_ids", nargs="+", type=int)

    def handle(self, *args, **options):
        try:
            with open(GROUPS_FILE_PATH, mode="r", encoding="utf-8") as csv_file:
                csv_reader = csv.DictReader(csv_file, delimiter=";")
                session = get_authenticated_session()
                for row in csv_reader:
                    if row["Статус"] not in GROUP_STATUSES_LIST or row["Тип группы"] not in GROUP_TYPES_LIST:
                        continue

                    group_id = row['\ufeff"ID"']
                    group_name = row["Название"]
                    group_status = row["Статус"]
                    group_type = row["Тип группы"]
                    group_venue = row["Площадка"]
                    teacher_name = row["Преподаватель"]
                    teacher_id = None
                    
                    if teacher_name != "not_set":
                        detailed_group_resp = session.get(
                            f"https://lms.logikaschool.com/api/v1/group/{group_id}?expand=venue%2Cteacher%2Ccurator%2Cbranch"
                        )
                        if detailed_group_resp.status_code == 200:
                            detailed_group_data = detailed_group_resp.json()["data"]
                            if detailed_group_data.get("teacher"):
                                teacher_id = detailed_group_data["teacher"]["id"]
                            else:
                                teacher_id = None

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
                            self.stdout.write(self.style.WARNING(f"Group {group_name} already exists. Updated data."))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"Group {group_name} duplicated or another error: {e}"))
        except FileNotFoundError:
            raise CommandError('File "path_to_your_file.csv" does not exist')
