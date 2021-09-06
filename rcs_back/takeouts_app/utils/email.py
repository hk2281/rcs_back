from datetime import timedelta
from typing import List
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils import timezone

from rcs_back.containers_app.models import Building, Container
from rcs_back.takeouts_app.models import TankTakeoutCompany


def takeout_condition_met_notify(building: Building,
                                 containers: List[Container]) -> None:
    """Оповещение о необходимости сбора"""
    if building.itmo_worker_email:

        email = building.itmo_worker_email
        itmo_worker_name = building.itmo_worker_name
        FRONT_LINK = "https://rcs-itmo.ru/takeouts"  # FIXME
        due_date = timezone.now().date() + timedelta(days=1)

        msg = render_to_string("takeout_condition_met.html", {
            "itmo_worker_name": itmo_worker_name,
            "due_date": due_date,
            "containers": containers,
            "front_link": FRONT_LINK,
            "has_building_parts": hasattr(building, "building_parts")
        }
        )

        email = EmailMessage(
            "Оповещание от сервиса RCS",
            msg,
            "noreply@rcs-itmo.ru",
            [email]
        )
        email.content_subtype = "html"
        email.send()


def tank_takeout_notify(building: Building) -> None:
    """Отправляет запрос на вывоз накопительного бака"""
    tank_takeout_company = TankTakeoutCompany.objects.first()
    if tank_takeout_company and tank_takeout_company.email:

        msg = render_to_string("tank_takeout.html", {
            "address": building.address,
            "phone": building.itmo_worker_phone,
            "name": building.itmo_worker_name
        }
        )

        email = EmailMessage(
            "Оповещание от сервиса RCS",
            msg,
            "noreply@rcs-itmo.ru",
            [tank_takeout_company.email]
        )
        email.content_subtype = "html"
        email.send()
