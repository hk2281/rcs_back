from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models.query import QuerySet
from typing import List

from rcs_back.containers_app.models import Building
from rcs_back.users_app.models import User


def get_eco_emails() -> List[str]:
    """Список email'ов экологов"""
    ecos = get_user_model().objects.filter(
        groups__name=settings.ECO_GROUP
    )
    emails = []
    for eco in ecos:
        emails.append(eco.email)
    return emails


def get_hoz_workers(building: Building = None) -> QuerySet[User]:
    """QuerySet из сотрудников хоз отдела
    (опционально - по зданию)"""
    hoz_workers = User.objects.filter(
        groups__name=settings.HOZ_GROUP
    )
    if building:
        hoz_workers = hoz_workers.filter(
            building=building
        )
    return hoz_workers


def building_worker_emails(building: Building) -> List[str]:
    """Возвращает email всех сотрудников эко отдела
    и email коменданта здания"""
    emails = get_eco_emails()
    hoz_worker = get_hoz_workers(building=building).first()
    if hoz_worker:
        emails.append(hoz_worker.email)
    return emails
