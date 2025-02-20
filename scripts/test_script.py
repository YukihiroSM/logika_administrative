import logging
from logika_statistics.models import Group
from logika_teachers.models import PredictedChurn, TeacherComment
from logika_teachers.repositories.churn_repository import ChurnRepository
from logika_teachers.repositories.dtos import ChurnRawDTO
from logika_statistics.models import OfficeRegion
import time

regions = [
    ("UA_Kievskaya oblast", "UA_Kievskaya oblast"),
    ("UA_Kiev", "UA_Kiev"),
    ("UA_Odessa", "UA_Odessa"),
    ("UA_Kharkov", "UA_Kharkov"),
    ("UA_Dnepr", "UA_Dnepr"),
    ("UA_SaaS", "UA_SaaS"),
    ("UA_Odesskaya oblast", "UA_Odesskaya oblast"),
    ("UA_Vynnytsya", "UA_Vynnytsya"),
    ("UA_Dnepropetrovskaya oblast", "UA_Dnepropetrovskaya oblast"),
    ("UA_Chernivtsi", "UA_Chernivtsi"),
    ("UA_Lviv", "UA_Lviv"),
    ("UA_ChernivtsiOblast", "UA_ChernivtsiOblast"),
    ("UA_LvivOblast", "UA_LvivOblast"),
    ("UA_VynnytsyaOblast", "UA_VynnytsyaOblast"),
    ("UA_Dnepr_region", "UA_Dnepr_region"),
    ("UA_Poltava", "UA_Poltava"),
    ("UA_Chernigov_obl", "UA_Chernigov_obl"),
    ("UA_Donetskobl", "UA_Donetskobl"),
    ("UA_Center", "UA_Center"),
    ("UA_Nikolaevskaya_obl", "UA_Nikolaevskaya_obl"),
    ("UA_Dnepropetrovskaya oblast2", "UA_Dnepropetrovskaya oblast2"),
]


def run():
    for reg in regions:
        OfficeRegion.objects.create(name=reg[0])
