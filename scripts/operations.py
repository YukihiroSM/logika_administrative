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
        ("2023-11-01", "2023-11-05"),
        ("2023-11-06", "2023-11-12"),
        ("2023-11-13", "2023-11-19"),
        ("2023-11-20", "2023-11-26"),
        ("2023-11-27", "2023-11-30"),
        ("2023-12-01", "2023-12-03"),
        ("2023-12-04", "2023-12-10"),
        ("2023-12-11", "2023-12-17"),
    ]

    start_dates = [line[0] for line in timelines]
    os.environ["start_dates"] = json.dumps(start_dates)
    month = "Лютий"
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
        # management.call_command("process_mk")
        # management.call_command("payments_process", course="programming")
        # management.call_command("payments_process", course="english")
        # management.call_command("generate_reports")

        management.call_command("process_master_classes")
        management.call_command("process_payments", course="programming")
        management.call_command("process_payments", course="english")
