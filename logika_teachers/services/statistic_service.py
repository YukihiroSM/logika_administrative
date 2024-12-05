from abc import ABC, abstractmethod
from datetime import datetime
from typing import Type

from logika_statistics.models import Location
from logika_teachers.repositories.dtos import MKReportDTO
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


class StatisticService(StatisticServiceInterface):

    def collect_statistic(self, start_date: str, end_date: str):
        for mk_service in self.master_class_services:
            mk_service.collect_master_classes(start_date, end_date)

        for payment_service in self.payments_services:
            payment_service.collect_payments(start_date, end_date)

    def get_master_class_reports(self, start_date: datetime) -> list[MKReportDTO]:
        locations = Location.objects.all()
        reports = list()
        for mk_service in self.master_class_services:
            data = mk_service.get_master_class_report(start_date)
            report = MKReportDTO(service_name=mk_service.__servicename__,
                                 mk_data=data,
                                 total_mk=sum(item["count"] for item in data))
            reports.append(report)

        for location in locations:
            for report in reports:
                master_classes_count = report.mk_data
                regional_manager = location.regional_manager
                territorial_manager = location.territorial_manager
                lms_location_name = location.lms_location_name
                location_count = next(
                    (item['count'] for item in master_classes_count if item['location'] == lms_location_name), 0
                )
                location_attended = next(
                    (item['count'] for item in master_classes_count if item['location'] == lms_location_name and
                     item['attended']), 0
                )
                territorial_count = sum(
                    item['count'] for item in master_classes_count if
                    item['territorial_manager'] == territorial_manager)
                regional_count = sum(
                    item['count'] for item in master_classes_count if item['regional_manager'] == regional_manager)

                if location_count <= 0:
                    continue

                if regional_manager not in report.location_data:
                    report.location_data[regional_manager] = (
                        regional_count, {territorial_manager: (territorial_count, {location: (location_count,
                                                                                              location_attended)})})
                elif territorial_manager not in report.location_data[regional_manager][1]:
                    report.location_data[regional_manager][1][territorial_manager] = (
                        territorial_count, {location: (location_count,
                                                       location_attended)})
                else:
                    report.location_data[regional_manager][1][territorial_manager][1][location] = (location_count,
                                                                                                   location_attended)

        return reports


if __name__ == "__main__":
    mk_service = MasterClassService(LMSService, MasterClassRepository)
    pm_service = PaymentService()
    statistic_service = StatisticService([mk_service], [pm_service])
