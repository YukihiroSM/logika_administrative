from abc import ABC, abstractmethod
from typing import Type

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
    def generate_report(self):
        pass


class StatisticService(StatisticServiceInterface):

    def collect_statistic(self, start_date: str, end_date: str):
        for mk_service in self.master_class_services:
            mk_service.collect_master_classes(start_date, end_date)

        for payment_service in self.payments_services:
            payment_service.collect_payments(start_date, end_date)

    def generate_report(self):
        pass


if __name__ == "__main__":
    mk_service = MasterClassService(LMSService)
    pm_service = PaymentService()
    statistic_service = StatisticService([mk_service], [pm_service])
