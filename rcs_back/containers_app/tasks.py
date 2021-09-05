import time

from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils import timezone
from celery import shared_task
from tempfile import NamedTemporaryFile

from rcs_back.containers_app.models import (
    FullContainerReport, Container, BuildingPart)
from rcs_back.takeouts_app.utils.email import takeout_condition_met_notify
from rcs_back.containers_app.utils.qr import generate_sticker
from rcs_back.takeouts_app.models import MassTakeoutConditionCommit


@shared_task
def public_container_add_notify(container_id: int) -> None:
    """Отправляет сообщение с инструкциями для активации
    добавленного контейнера"""
    time.sleep(10)  # Ждём сохранения в БД
    container = Container.objects.get(pk=container_id)
    is_ecobox = container.kind == Container.ECOBOX

    msg = render_to_string("public_container_add.html", {
        "is_ecobox": is_ecobox,
        "container_room": container.building.get_container_room,
        "sticker_room": container.building.get_sticker_room
    }
    )

    email = EmailMessage(
        "Добавление контейнера в сервисе RCS",
        msg,
        "noreply@rcs-itmo.ru",
        [container.email]
    )
    email.content_subtype = "html"
    with NamedTemporaryFile() as tmp:
        sticker_im = generate_sticker(container_id)
        sticker_im.save(tmp.name, "png", quality=100)
        email.attach_file(tmp.name)
        email.send()


def check_mass_condition_to_notify(container: Container) -> None:
    """Проверяем, нужно ли отправить оповещение для сбора контейнеров.
    Если условие по массе выполняется, то оповещаем и фиксируем выполнение."""
    trigger = container.get_mass_rule_trigger()
    if trigger:
        """Выполняется условие по массе"""
        if not trigger.is_mass_condition_commited():
            """Нет коммита выполнения"""
            building_part = container.building_part if isinstance(
                trigger, BuildingPart) else None
            MassTakeoutConditionCommit.objects.create(
                building=container.building,
                building_part=building_part
            )

        takeout_condition_met_notify(
            trigger.get_building(),
            trigger.containers_for_takeout()
        )


@shared_task
def handle_first_full_report(container_id: int, by_staff: bool) -> None:
    """При заполнении контейнера нужно запомнить время
    и пересчитать среднее время заполнения"""
    container = Container.objects.get(pk=container_id)
    FullContainerReport.objects.create(
        container=container,
        by_staff=by_staff
    )

    time.sleep(10)  # Ждём сохранения в БД

    container.avg_fill_time = container.calc_avg_fill_time()

    """Если выполняются условия для вывоза по
    кол-ву бумаги, сообщаем"""
    if by_staff or container.is_reported_just_enough():
        container._is_full = True  # Для сортировки
        check_mass_condition_to_notify(container)
    container.save()


@shared_task
def handle_repeat_full_report(container_id: int, by_staff: bool) -> None:
    """При повторном сообщении о заполнении нужно
    увеличить кол-во сообщений"""
    container = Container.objects.get(pk=container_id)
    report = container.last_full_report()
    if by_staff:
        report.by_staff = True
    else:
        report.count += 1
    report.save()

    time.sleep(10)  # Ждём сохранения в БД

    """Если выполняются условия для вывоза по
    кол-ву бумаги, сообщаем"""
    if by_staff or container.is_reported_just_enough():
        container._is_full = True  # Для сортировки
        container.save()
        check_mass_condition_to_notify(container)


@shared_task
def handle_empty_container(container_id: int) -> None:
    """При опустошении контейнера нужно запомнить время
    и пересчитать среднее время выноса"""
    container = Container.objects.get(pk=container_id)
    last_full_report = container.last_full_report()
    if last_full_report:
        last_full_report.emptied_at = timezone.now()
        last_full_report.save()
        time.sleep(10)  # Ждём сохранения в БД
        container.avg_takeout_wait_time = container.calc_avg_takeout_wait_time()
    container._is_full = False  # Для сортировки
    container.save()
