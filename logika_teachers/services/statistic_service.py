from abc import ABC, abstractmethod
from datetime import datetime
from typing import Type

from logika_statistics.models import Location
from logika_teachers.repositories.dtos import MKReportDTO, PMReportDTO
from logika_teachers.repositories.master_class_repository import MasterClassRepository
from logika_teachers.services.lms_service import LMSService
from logika_teachers.services.master_class_service import MasterClassServiceInterface, MasterClassService
from logika_teachers.services.one_c_service import PaymentServiceInterface, PaymentService


class StatisticServiceInterface(ABC):

    def __init__(self,
                 master_class_services: list[MasterClassServiceInterface],
                 payments_services: list[PaymentServiceInterface]):
        self.master_class_services = master_class_services
        self.payments_services = payments_services

    @abstractmethod
    def collect_statistic(self, start_date: str, end_date: str):
        pass

    @abstractmethod
    def get_master_class_reports(self, start_date: datetime) -> list[MKReportDTO]:
        pass


class StatisticService(StatisticServiceInterface):

    def collect_statistic(self, start_date: str, end_date: str):
        for mk_service in self.master_class_services:
            mk_service.collect_master_classes(start_date, end_date)

        for payment_service in self.payments_services:
            payment_service.collect_payments(start_date, end_date)

    def _count_location(self, location: Location, report: MKReportDTO, pm_report: PMReportDTO) -> tuple:
        master_classes_count = report.mk_data
        pm_count = pm_report.pm_data
        lms_location_name = location.lms_location_name
        location_count = next(
            (item['count'] for item in master_classes_count if item['location'] == lms_location_name), 0
        )
        location_attended = next(
            (item['count'] for item in master_classes_count if item['location'] == lms_location_name and
             item['attended']), 0
        )
        location_payments = next(
            (item['count'] for item in pm_count if item['location'] == lms_location_name), 0
        )
        location_conversion = (location_payments / location_attended) * 100 if location_attended != 0 else 0

        return location_count, location_attended, location_payments, location_conversion

    def _count_territorial(self, location: Location, report: MKReportDTO, pm_report: PMReportDTO) -> tuple:
        master_classes_count = report.mk_data
        pm_count = pm_report.pm_data
        territorial_manager = location.territorial_manager
        territorial_count = sum(
            item['count'] for item in master_classes_count if
            item['territorial_manager'] == territorial_manager)
        territorial_attended = sum(
            item['count'] for item in master_classes_count if
            item['territorial_manager'] == territorial_manager and item['attended'])
        territorial_payments = sum(
            item['count'] for item in pm_count if
            item['territorial_manager'] == territorial_manager)
        territorial_conversion = (territorial_payments / territorial_attended) * 100 if territorial_attended != 0 else 0

        return territorial_count, territorial_attended, territorial_payments, territorial_conversion

    def _count_regional(self, location: Location, report: MKReportDTO, pm_report: PMReportDTO) -> tuple:
        master_classes_count = report.mk_data
        pm_count = pm_report.pm_data
        regional_manager = location.regional_manager
        regional_count = sum(
            item['count'] for item in master_classes_count if item['regional_manager'] == regional_manager)
        regional_attended = sum(
            item['count'] for item in master_classes_count if
            item['regional_manager'] == regional_manager and item['attended'])
        regional_payments = sum(
            item['count'] for item in pm_count if
            item['regional_manager'] == regional_manager)
        regional_conversion = (regional_payments / regional_attended) * 100 if regional_attended != 0 else 0

        return regional_count, regional_attended, regional_payments, regional_conversion

    def get_master_class_reports(self, start_date: datetime) -> list[MKReportDTO]:
        locations = Location.objects.all()
        mk_reports = list()
        for mk_service in self.master_class_services:
            data = mk_service.get_master_class_report(start_date)
            report = MKReportDTO(service_name=mk_service.__servicename__,
                                 mk_data=data,
                                 total_mk=sum(item["count"] for item in data))
            mk_reports.append(report)

        pm_reports = list()
        for pm_service in self.payments_services:
            data = pm_service.get_reports(start_date)
            report = PMReportDTO(pm_data=data, total_pm=sum(item["count"] for item in data))
            pm_reports.append(report)

        pm_report = pm_reports[0]
        for location in locations:
            for report in mk_reports:
                lms_location_name = location.lms_location_name
                territorial_manager = location.territorial_manager
                regional_manager = location.regional_manager
                location_count = self._count_location(location, report, pm_report)
                territorial_count = self._count_territorial(location, report, pm_report)
                regional_count = self._count_regional(location, report, pm_report)

                if location_count[0] <= 0:
                    continue

                if regional_manager not in report.location_data:
                    report.location_data[regional_manager] = (
                        regional_count, {territorial_manager: (territorial_count, {location: location_count})})
                elif territorial_manager not in report.location_data[regional_manager][1]:
                    report.location_data[regional_manager][1][territorial_manager] = (
                        territorial_count, {location: location_count})
                else:
                    report.location_data[regional_manager][1][territorial_manager][1][location] = location_count

        return mk_reports


if __name__ == "__main__":
    mk_service = MasterClassService(LMSService, MasterClassRepository)
    pm_service = PaymentService()
    statistic_service = StatisticService([mk_service], [pm_service])
