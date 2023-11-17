from django.core import management
from logika_administrative.settings import BASE_DIR
import os
import logging
import datetime
from pathlib import Path
import json
from logika_statistics.models import StudentReport, Location
from utils.lms_authentication import get_authenticated_session
from concurrent.futures import ThreadPoolExecutor
import pandas as pd


def run():
    locations_in_reports = list(set(StudentReport.objects.values_list("location")))
    locations = list(set(Location.objects.values_list("lms_location_name")))
    for loc in locations_in_reports:
        if loc not in locations:
            print(loc)
