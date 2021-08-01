from typing import List
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model

from rcs_back.containers_app.models import Building, BuildingPart


def get_hoz_emails() -> List[str]:
    """Список email'ов хоз отдела"""
    hozs = get_user_model().objects.filter(
        groups__name=settings.HOZ_GROUP
    )
    emails = []
    for hos in hozs:
        emails.append(hos.email)
    return emails


def takeout_condition_met_notify(building: Building,
                                 building_part: BuildingPart = None) -> None:
    """Оповещение о необходимости сбора"""
    pass


def containers_takeout_notify(building: Building,
                              building_part: BuildingPart = None) -> None:
    """Отправляет запрос на сбор контейнеров"""
    msg = (f"По адресу {building}")
    if building_part:
        msg += f", {building_part} "
    msg += ("заполнилось достаточно контейнеров для выноса. "
            "Список контейнеров:\n\n")
    if building_part:
        containers = building_part.containers_for_takeout()
    else:
        containers = building.containers_for_takeout()
    for container in containers:
        msg += container.full_location()  # FIXME
        msg += ".\n"
    send_mail(
        "Оповещание от сервиса RCS",
        msg,
        "noreply@rcs-itmo.ru",
        [TANK_TAKEOUT_EMAIL]  # FIXME
    )


def tank_takeout_notify(building: Building) -> None:
    """Отправляет запрос на вывоз накопительного бака"""
    TANK_TAKEOUT_EMAIL = "tank@takeout.com"
    msg = (f"В накопительном баке по адресу {building} "
           "накопилось достаточно макулатуры для вывоза.")
    send_mail(
        "Оповещание от сервиса RCS",
        msg,
        "noreply@rcs-itmo.ru",
        [TANK_TAKEOUT_EMAIL]
    )
