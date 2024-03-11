from django.core import management
from logika_administrative.settings import BASE_DIR
import os
import logging
import datetime
from pathlib import Path
import json
from logika_statistics.models import StudentReport, Location, MasterClassRecord, PaymentRecord
from utils.lms_authentication import get_authenticated_session
from concurrent.futures import ThreadPoolExecutor
import pandas as pd


def run():
    start_dates = [
        "2024-02-01","2024-02-05", "2024-02-12", "2024-02-19", "2024-02-26"
    ]
    locations_in_mc = MasterClassRecord.objects.filter(start_date__in=start_dates).values_list("location", flat=True)
    locations_in_payments = PaymentRecord.objects.filter(start_date__in=start_dates).values_list("location", flat=True)

    locations_in_mc = list(set(locations_in_mc))
    locations_in_payments = list(set(locations_in_payments))

    real_locations = Location.objects.values_list("lms_location_name", flat=True)

    print("Локации, по которым есть МК:")
    for location in locations_in_mc:
        if not (location in real_locations):
            print("\t", location)

    print("Локации, по которым есть оплаты:")
    for location in locations_in_payments:
        if not (location in real_locations):
            print("\t", location)





