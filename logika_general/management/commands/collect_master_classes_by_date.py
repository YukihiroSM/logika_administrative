from django.core.management.base import BaseCommand, CommandParser
from datetime import datetime

from utils.lms_authentication import get_authenticated_session


class Command(BaseCommand):
    help = "Collect master classes by date"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "-sd", "--start_date", type=str, help="Starting Date in format YYYY-MM-DD"
        )

        parser.add_argument(
            "-ed", "--end_date", type=str, help="Ending Date in format YYYY-MM-DD"
        )

    def handle(self, *args, **options):
        start_date = options.get("start_date")
        end_date = options.get("end_date")
        if not start_date or not end_date:
            print(
                "Collecting data for today, because the date is not specified:",
                datetime.today().strftime("%Y-%m-%d"),
            )
            start_date = end_date = datetime.today().strftime("%Y-%m-%d")

        print("Collecting data for the period:", start_date, end_date)

        session = get_authenticated_session()
        groups_resp = session.get(
            f"https://lms.logikaschool.com/group/default/schedule?start_time%5D={start_date} - {end_date}"
        )
        print(groups_resp.text)
