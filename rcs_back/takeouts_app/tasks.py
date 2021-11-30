import datetime
from typing import List

from celery import shared_task
from dateutil.relativedelta import relativedelta
# from django.core.mail import EmailMessage
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.template.loader import render_to_string
from django.utils import timezone

from rcs_back.containers_app.models import Building, Container
from rcs_back.takeouts_app.models import TankTakeoutRequest


@shared_task
def check_time_conditions() -> None:
    '''Выполнены ли условия "не больше N дней"'''
    building: Building
    for building in Building.objects.all():
        building.check_conditions_to_notify()


def get_total_mass(start_date: datetime.date, end_date: datetime.date) -> int:
    """Возвращает массу, собранную сервисом
    за промежуток времени"""

    collected_mass = TankTakeoutRequest.objects.filter(
        confirmed_mass__isnull=False
    ).filter(
        confirmed_at__gte=start_date,
        confirmed_at__lt=end_date
    ).aggregate(
        collected_mass=Coalesce(Sum("confirmed_mass"), 0)
    )["collected_mass"]

    return collected_mass


def get_container_owner_emails() -> List[str]:
    """Возвращает список уникальных email'ов
    пользователей сервиса."""
    return list(Container.objects.exclude(
        email__isnull=True
    ).exclude(email__exact="").filter(
        status=Container.ACTIVE
    ).values_list("email", flat=True).distinct())


def get_collected_mass_per_owner(owners: List[str],
                                 start_date: datetime.date,
                                 end_date: datetime.date) -> "dict[str, int]":
    """Возвращает кол-во собранной макулатуры
    каждым из пользователей сервиса"""
    res = {}
    for owner_email in owners:
        collected_mass = 0
        containers = Container.objects.filter(
            email=owner_email
        ).filter(
            status=Container.ACTIVE
        )
        container: Container
        for container in containers:
            collected_mass += container.collected_mass(start_date, end_date)
        res[owner_email] = collected_mass
    return res


def get_collected_mass_percentage(email: str,
                                  collected_mass: "dict[str, int]") -> int:
    """Возвращает процент пользователей, у которых собранная масса меньше,
    чем у данного"""
    if len(collected_mass.keys()) > 1:
        less = 0
        for user in collected_mass:
            if collected_mass[user] < collected_mass[email]:
                less += 1
        res = (less / len(collected_mass.keys())) * 100 // 1
        return res
    else:
        return 100


def collected_mass_mailing() -> None:
    """Рассылка раз в три месяца о кол-ве собранной макулатуры."""
    emails = get_container_owner_emails()
    end_date = timezone.now().date().replace(day=1)
    start_date = end_date - relativedelta(months=3)
    total_mass = get_total_mass(start_date, end_date)
    collected_mass_per_owner = get_collected_mass_per_owner(
        emails,
        start_date,
        end_date
    )

    for user_email in emails:
        containers = Container.objects.filter(
            email=user_email
        ).filter(
            status=Container.ACTIVE
        )
        if len(containers) == 1:
            container_ids = f"контейнера с ID {containers[0].pk}"
        else:
            container_ids = "контейнеров с ID "
            for container in containers:
                container_ids += f"{container.pk}, "
            container_ids = container_ids[:len(container_ids)-2]
        building_mass = containers[0].building.confirmed_collected_mass(
            start_date=start_date, end_date=end_date
        )
        msg = render_to_string("collected_mass_mailing.html", {
            "start_date": start_date,
            "end_date": end_date,
            "total_mass": total_mass,
            "building_mass": building_mass,
            "container_mass": collected_mass_per_owner[user_email],
            "container_ids": container_ids,
            "percentage": get_collected_mass_percentage(
                user_email,
                collected_mass_per_owner
            )
        }
        )
        print(msg)
        # email = EmailMessage(
        #     "Оповещение от сервиса RecycleStarter",
        #     msg,
        #     None,
        #     [user_email]
        # )
        # email.content_subtype = "html"
        # email.send()
