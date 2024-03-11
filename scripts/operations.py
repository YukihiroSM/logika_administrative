import datetime
import json
import logging
import os
from pathlib import Path

from django.core import management

from logika_administrative.settings import BASE_DIR


def run():
    logger = logging.getLogger(__name__)
    timelines = [
        ("2024-03-01", "2024-03-03"),
        ("2024-03-04", "2024-03-10"),
        ("2024-03-01", "2024-03-10"),

    ]



    start_dates = [line[0] for line in timelines]
    os.environ["start_dates"] = json.dumps(start_dates)
    month = "Лютий"
    # management.call_command("update_locations")
    for timeline in timelines:
        lms_reports_path = Path(
            BASE_DIR, "lms_reports", month, f"{timeline[0]}_{timeline[1]}"
        )
        one_c_reports_path = Path(
            BASE_DIR, "1c_reports", month, f"{timeline[0]}_{timeline[1]}"
        )
        lms_reports_path.mkdir(parents=True, exist_ok=True)
        one_c_reports_path.mkdir(parents=True, exist_ok=True)
        logger.debug(
            f"STARTING GETTING REPORT FOR {str(timeline)}"
            + str(datetime.datetime.now())
        )
        os.environ["start_date"] = timeline[0]
        os.environ["end_date"] = timeline[1]
        os.environ["month"] = month
        # management.call_command("process_master_classes")
        # management.call_command("process_payments", course="english")
        # management.call_command("process_payments", course="programming")
        management.call_command("generate_reports")

        
        # management.call_command("lesson_consolidation")
    # management.call_command("collect_groups_data")
