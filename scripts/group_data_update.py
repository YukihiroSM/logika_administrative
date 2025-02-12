from django.db import transaction

from logika_administrative import settings
from logika_teachers.repositories.group_repository import GroupRepository
from logika_teachers.services.group_service import GroupService
from logika_teachers.services.lms_service import LMSService
from logika_statistics.models import Group
from logika_teachers.models import PredictedChurn
import csv

GROUPS_FILE_PATH = settings.BASE_DIR / "groups_data.csv"


def run():
    # churns = PredictedChurn.objects.all()
    # for churn in churns:
    #     churn.group = None
    #     churn.save()

    # Group.objects.all().delete()
    group_service = GroupService(lms_service=LMSService, group_repository=GroupRepository)
    # success = 0
    # total = 0
    # errors = 0
    # with open(GROUPS_FILE_PATH, 'r', encoding='utf-8') as file:
    #     reader = csv.DictReader(file, delimiter=";")
    #     print(reader.fieldnames)
    #     for row in reader:
    #         group_id = row['Group ID']
    #         group, created = group_service.get_or_create_group(group_id)
    #         total += 1
    #         if created:
    #             print(f"Group {group.title} created")
    #             success += 1
    #         elif group and not created:
    #             print(f"Group {group.title} has been found")
    #         else:
    #             print(f"Group {group_id} did not create")
    #             errors += 1

    #     print("success", success)
    #     print("errors", errors)
    #     print("total", total)

    # churns = PredictedChurn.objects.all()
    # for churn in churns:
    #     churn.save()
    group, created = group_service.get_or_create_group(1598389)
    print(group, created)
