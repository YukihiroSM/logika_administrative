import logging
import os
from datetime import datetime
import library
from django.core.management.base import BaseCommand

from logika_statistics.models import ClientManagerReport, LocationReport, StudentReport, CourseReport, Location, TeacherReportNew


class Command(BaseCommand):
    help = 'Does some magical work'

    def __init__(self):
        super().__init__()
        self.lms_file_obj = None
        self.one_c_file_obj = None
        self.logger = logging.getLogger(__name__)

    def message(self, msg):
        self.logger.debug(str(msg) + " " + str(datetime.now()))

    @staticmethod
    def get_conversion(payments, attended):
        conversion = None
        if payments == 0 and attended == 0:
            conversion = 0
        else:
            try:
                conversion = round((payments / attended) * 100, 2)
            except ZeroDivisionError:
                conversion = 100
        return conversion if conversion else 0

    @staticmethod
    def get_rm_by_cm(client_manager, start_date, end_date):
        regionals = StudentReport.objects.filter(
            start_date__gte=start_date, end_date__lte=end_date, business="programming", client_manager=client_manager).values_list("regional_manager", flat=True).distinct()
        return set(regionals)

    @staticmethod
    def get_rm_by_tm(tm, start_date, end_date):
        regionals = StudentReport.objects.filter(
            start_date__gte=start_date, end_date__lte=end_date, business="programming", territorial_manager=tm).values_list("regional_manager", flat=True).distinct()
        return set(regionals)

    @staticmethod
    def get_rm_by_location(location, start_date, end_date):
        regionals = StudentReport.objects.filter(
            start_date__gte=start_date, end_date__lte=end_date, business="programming", location=location).values_list("regional_manager", flat=True).distinct()
        return set(regionals)

    def handle(self, *args, **options):
        start_date = datetime.strptime(
            os.environ.get("start_date"), "%Y-%m-%d").date()
        end_date = datetime.strptime(
            os.environ.get("end_date"), "%Y-%m-%d").date()
        reports = StudentReport.objects.filter(
            start_date__gte=start_date, end_date__lte=end_date, business="programming")
        territorial_managers = reports.values_list(
            "territorial_manager", flat=True).distinct()
        regional_managers = reports.values_list(
            "regional_manager", flat=True).distinct()
        client_managers = reports.values_list(
            "client_manager", flat=True).distinct()
        locations = reports.values_list("location", flat=True).distinct()
        for regional_manager in regional_managers:
            for territorial_manager in territorial_managers:
                if not (regional_manager in self.get_rm_by_tm(territorial_manager, start_date, end_date)):
                    continue
                for client_manager in client_managers:
                    if not (regional_manager in self.get_rm_by_cm(client_manager, start_date, end_date)):
                        continue
                    payments = len(reports.filter(business="programming", client_manager=client_manager,
                                                  territorial_manager=territorial_manager,
                                                  regional_manager=regional_manager, payment=1).all())
                    attended_mc = len(reports.filter(business="programming", client_manager=client_manager,
                                                     territorial_manager=territorial_manager,
                                                     regional_manager=regional_manager, attended_mc=1).exclude(
                        amo_id__isnull=True, is_duplicate=1).all())
                    enrolled_mc = len(reports.filter(business="programming", client_manager=client_manager,
                                                     territorial_manager=territorial_manager,
                                                     regional_manager=regional_manager, enrolled_mc=1).exclude(
                        amo_id__isnull=True, is_duplicate=1).all())
                    conversion = self.get_conversion(payments, attended_mc)
                    new_report = ClientManagerReport(
                        client_manager=client_manager,
                        territorial_manager=territorial_manager,
                        regional_manager=regional_manager,
                        business="programming",
                        total_attended=attended_mc,
                        total_payments=payments,
                        conversion=conversion,
                        total_enrolled=enrolled_mc,
                        start_date=start_date,
                        end_date=end_date
                    )
                    print(
                        f"Regional Manager: {regional_manager}, Territorial Manager: {territorial_manager}, Client Manager: {client_manager}"
                        f"Payments: {payments}, Attended: {attended_mc}, Enrolled: {enrolled_mc}, Conversion: {conversion}")
                    new_report.save()

                for location in locations:
                    if not (regional_manager in self.get_rm_by_location(location, start_date, end_date)):
                        continue
                    payments = len(reports.filter(business="programming", location=location,
                                                  territorial_manager=territorial_manager,
                                                  regional_manager=regional_manager, payment=1).all())
                    attended_mc = len(reports.filter(business="programming", location=location,
                                                     territorial_manager=territorial_manager,
                                                     regional_manager=regional_manager, attended_mc=1).exclude(
                        amo_id__isnull=True, is_duplicate=1).all())
                    enrolled_mc = len(reports.filter(business="programming", location=location,
                                                     territorial_manager=territorial_manager,
                                                     regional_manager=regional_manager, enrolled_mc=1).exclude(
                        amo_id__isnull=True, is_duplicate=1).all())
                    conversion = self.get_conversion(payments, attended_mc)
                    new_report = LocationReport(
                        location_name=location,
                        territorial_manager=territorial_manager,
                        regional_manager=regional_manager,
                        business="programming",
                        total_attended=attended_mc,
                        total_payments=payments,
                        conversion=conversion,
                        total_enrolled=enrolled_mc,
                        start_date=start_date,
                        end_date=end_date
                    )
                    print(
                        f"Regional Manager: {regional_manager}, Territorial Manager: {territorial_manager}, Location: {location}"
                        f"Payments: {payments}, Attended: {attended_mc}, Enrolled: {enrolled_mc}, Conversion: {conversion}")
                    new_report.save()
