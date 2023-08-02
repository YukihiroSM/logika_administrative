from django.core.management.base import BaseCommand, CommandParser
from django.contrib.contenttypes.models import ContentType
from datetime import datetime
from utils.exceptions import LmsGroupCollectionFailed
from utils.lms_authentication import get_authenticated_session

from logika_general.models import Group, Location, Notification


class Command(BaseCommand):
    help = "Collect master classes by date"

    def handle(self, *args, **options):
        print(
            "Collecting groups list. Action datetime:",
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )
        session = get_authenticated_session()
        groups_resp = session.get("https://lms.logikaschool.com/api/v1/group")
        if groups_resp.status_code != 200:
            print("Groups collection failed, aborting the process")
            raise LmsGroupCollectionFailed(
                "Unable to collect groups. API response: ",
                groups_resp.status_code,
                groups_resp.text,
            )

        print("Groups collection successful")
        groups_data = groups_resp.json()["data"]["items"]
        for group in groups_data:
            group_dict = {
                "id": group["id"],
                "title": group["title"],
                "venue": group["venue"] if group["venue"] else "Unknown",
                "teacher_name": group["teacherName"]
                if group["teacherName"]
                else "Unknown",
                "type": group["type"]["value"],
                "status": group["status"]["value"],
            }
            print(group_dict)
            if group["venue"] != "Unknown" and group["venue"] is not None:
                location, created = Location.objects.update_or_create(
                    lms_location_name=group["venue"],
                )
                if created:
                    Notification.objects.create(
                        title="Нова локація в базі",
                        body=(
                            f"Додано нову локацію в базу даних: {location}."
                            f"Перейдіть в локацію та заповніть необхідні дані."
                        ),
                        object_id=location.id,
                        content_type=ContentType.objects.get_for_model(location),
                    )

            group_obj, created = Group.objects.update_or_create(
                lms_id=group["id"], defaults=group_dict
            )
