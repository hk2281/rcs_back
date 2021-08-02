from typing import List
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model

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
                                 building: Building = None,
                                 building_part: BuildingPart = None) -> None:
    """Оповещение о необходимости сбора"""
    if (building and building.itmo_worker_email or
            building_part and building_part.building.itmo_worker_email):

        if building:
            msg = f"По адресу {building.address} "
            containers = building.containers_for_takeout()

        elif building_part:
            msg = f"По адресу {building_part.building.address}, {building_part} "
            containers = building_part.containers_for_takeout()

        msg += "нужно провести сбор макулатуры, так как "

        if short_condition == "mass":
            condition = "собранная маса превышает заданную правилом."
        else:
            condition = "время, прошедшее после очищения контейнеров, превышает заданное правилом."
        msg += condition
        msg += "\n\n"

        msg += "Cписок контейнеров для сбора:\n"
        for container in containers:
            msg += f"Этаж {container.floor}"
            msg += ", "
            msg += container.location
            msg += ".\n"

        if building:
            email = building.itmo_worker_email
        elif building_part:
            email = building_part.building.itmo_worker_email
        send_mail(
            "Оповещание от сервиса RCS",
            msg,
            "noreply@rcs-itmo.ru",
            [email]
        )


def containers_takeout_notify(request: ContainersTakeoutRequest) -> None:
    """Отправляет запрос на сбор контейнеров"""
    if request.building.containers_takeout_email:
        msg = (f"По адресу {request.building} ")
        if request.building_part:
            msg += f", {request.building_part} "
        msg += ("заполнилось достаточно контейнеров для выноса. "
                "Расположение заполненных контейнеров:\n\n")
        for container in request.containers.all():
            msg += f"Этаж {container.floor}"
            msg += ", "
            msg += container.location
            msg += ".\n"

        send_mail(
            "Оповещание от сервиса RCS",
            msg,
            "noreply@rcs-itmo.ru",
            [request.building.containers_takeout_email]
        )


def tank_takeout_notify(building: Building) -> None:
    """Отправляет запрос на вывоз накопительного бака"""
    tank_takeout_email = TankTakeoutCompany.objects.first().email
    msg = (f"В накопительном баке по адресу {building} "
           "накопилось достаточно макулатуры для вывоза.")
    send_mail(
        "Оповещание от сервиса RCS",
        msg,
        "noreply@rcs-itmo.ru",
        [tank_takeout_email]
    )
