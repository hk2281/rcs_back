from typing import List
from django.core.mail import EmailMessage
from django.conf import settings
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string

from rcs_back.containers_app.models import Building, BuildingPart
from rcs_back.takeouts_app.models import (ContainersTakeoutRequest,
                                          TankTakeoutCompany)


def get_hoz_emails() -> List[str]:
    """Список email'ов хоз отдела"""
    hozs = get_user_model().objects.filter(
        groups__name=settings.HOZ_GROUP
    )
    emails = []
    for hos in hozs:
        emails.append(hos.email)
    return emails


def takeout_condition_met_notify(short_condition: str,
                                 building: Building,
                                 building_part: BuildingPart = None) -> None:
    """Оповещение о необходимости сбора"""
    if building.itmo_worker_email:

        address = building.address
        email = building.itmo_worker_email

        if building_part:
            address += ", "
            address += str(building_part)

            containers = building_part.containers_for_takeout()
        else:
            containers = building.containers_for_takeout()

        if short_condition == "mass":
            condition = ("масса собранной макулатуры "
                         "превышает заданную правилом")
        else:
            condition = (
                "время, прошедшее после очищения контейнеров,"
                " превышает заданное правилом"
            )

        msg = render_to_string("takeout_condition_met.html", {
            "address": address,
            "condition": condition,
            "containers": containers
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


def containers_takeout_notify(request: ContainersTakeoutRequest) -> None:
    """Отправляет запрос на сбор контейнеров"""
    if request.building.containers_takeout_email:

        msg = render_to_string("containers_takeout.html", {
            "building": request.building,
            "containers": request.containers.all(),
            "building_part": request.building_part
        }
        )

        email = EmailMessage(
            "Оповещание от сервиса RCS",
            msg,
            "noreply@rcs-itmo.ru",
            [request.building.containers_takeout_email]
        )
        email.content_subtype = "html"
        email.send()


def tank_takeout_notify(building: Building) -> None:
    """Отправляет запрос на вывоз накопительного бака"""
    tank_takeout_email = TankTakeoutCompany.objects.first().email
    if tank_takeout_email:

        msg = render_to_string("tank_takeout.html", {
            "address": building.address,
        }
        )

        email = EmailMessage(
            "Оповещание от сервиса RCS",
            msg,
            "noreply@rcs-itmo.ru",
            [tank_takeout_email]
        )
        email.content_subtype = "html"
        email.send()
