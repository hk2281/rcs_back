from datetime import timedelta
from typing import List
from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone

from rcs_back.containers_app.models import Building, Container, EmailToken
from rcs_back.takeouts_app.models import TankTakeoutCompany
from rcs_back.utils.model import *


def takeout_condition_met_notify(building: Building,
                                 containers: List[Container]) -> None:
    """Оповещение о необходимости сбора"""
    emails = building_worker_emails(building)
    if emails:

        due_date = timezone.now().date() + timedelta(days=1)
        token = EmailToken.objects.create()
        token.set_token()
        token.save()
        link = settings.DOMAIN + \
            f"/api/container-takeout-requests?token={token.token}&building={building.pk}"

        msg = render_to_string("takeout_condition_met.html", {
            "due_date": due_date,
            "containers": containers,
            "link": link,
            "has_building_parts": hasattr(building, "building_parts"),
        }
        )

        email = EmailMessage(
            "Оповещание от сервиса RCS",
            msg,
            "noreply@rcs-itmo.ru",
            emails
        )
        email.content_subtype = "html"
        email.send()


def tank_takeout_notify(building: Building) -> None:
    """Отправляет запрос на вывоз накопительного бака"""
    tank_takeout_company = TankTakeoutCompany.objects.first()
    if tank_takeout_company and tank_takeout_company.email:

        phone = ""
        name = ""
        hoz_worker = get_hoz_workers(building).first()
        if hoz_worker:
            phone = hoz_worker.phone
            name = hoz_worker.name

        msg = render_to_string("tank_takeout.html", {
            "address": building.address,
            "phone": phone,
            "name": name
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
