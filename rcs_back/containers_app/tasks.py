import datetime
import time

from django.core.cache import cache
from django.core.mail import send_mail
from django.utils import timezone
from celery import shared_task

from rcs_back.containers_app.models import (
    FullContainerReport, Container, Building, BuildingPart)
from rcs_back.containers_app.utils.email import get_public_container_add_msg
from rcs_back.takeouts_app.utils.email import takeout_condition_met_notify
from rcs_back.takeouts_app.models import MassTakeoutConditionCommit


def calc_avg_fill_time(container: Container) -> str:
    """Считаем среднее время заполнения контейнера"""
    reports = FullContainerReport.objects.filter(
        container=container
    ).order_by(
        "reported_full_at"
    )
    if len(reports) > 1:
        sum_time = datetime.timedelta(seconds=0)
        for i in range(len(reports) - 1):
            fill_time = reports[i+1].reported_full_at - reports[i].emptied_at
            sum_time += fill_time
        avg_fill_time = str(sum_time / (len(reports) - 1))
        # Сохраняем в кэш
        cache.set(f"{container.pk}_avg_fill_time", avg_fill_time, None)
        return f"container {container.pk}: {avg_fill_time}"
    else:
        return "Контейнер заполнился только первый раз"


def calc_avg_takeout_wait_time(container: Container) -> str:
    """Считаем среднее время ожидания выноса контейнера"""
    reports = FullContainerReport.objects.filter(
        container=container
    )
    if not len(reports) or (len(reports) == 1 and not reports[0].emptied_at):
        return "Недостаточно данных"
    else:
        sum_time = datetime.timedelta(seconds=0)
        for report in reports:
            takeout_wait_time = report.emptied_at - report.reported_full_at
            sum_time += takeout_wait_time
        avg_takeout_wait_time = str(sum_time / len(reports))
        # Сохраняем в кэш
        cache.set(f"{container.pk}_avg_takeout_wait_time",
                  avg_takeout_wait_time, None)
        return f"container {container.pk}: {avg_takeout_wait_time}"


@shared_task
def public_container_add_notify(container_id: int) -> None:
    """Отправляет сообщение с инструкциями для активации
    добавленного контейнера"""
    time.sleep(10)  # Ждём сохранения в БД и генерации стикера
    container = Container.objects.get(pk=container_id)
    msg = get_public_container_add_msg(container)
    send_mail(
        "Добавление контейнера в сервисе RCS",
        msg,
        "noreply@rcs-itmo.ru",
        [container.email]
    )


def check_mass_condition_to_notify(container: Container) -> None:
    """Проверяем, нужно ли отправить оповещение для сбора контейнеров.
    Если правило по массе выполняется, то оповещаем и фиксируем выполнение."""
    trigger = container.what_triggers_mass_rule()
    if trigger:
        takeout_condition_met_notify(building=container.building)

        if not trigger.is_mass_condition_commited():
            if isinstance(trigger, BuildingPart):
                MassTakeoutConditionCommit.objects.create(
                    building_part=container.building_part
                )
                takeout_condition_met_notify(
                    building_part=container.building_part)
            if isinstance(trigger, Building):
                MassTakeoutConditionCommit.objects.create(
                    building=container.building
                )


@shared_task
def handle_first_full_report(container_id: int) -> None:
    """При заполнении контейнера нужно запомнить время
    и пересчитать среднее время заполнения"""
    container = Container.objects.get(pk=container_id)
    FullContainerReport.objects.create(
        container=container
    )

    time.sleep(10)  # Ждём сохранения в БД
    calc_avg_fill_time(container)

    """Если выполняются условия для вывоза по
    кол-ву бумаги, сообщаем"""
    if container.is_reported_just_enough():
        check_mass_condition_to_notify(container)


@shared_task
def handle_repeat_full_report(container_id: int) -> None:
    """При повторном сообщении о заполнении нужно
    увеличить кол-во сообщений"""
    container = Container.objects.get(pk=container_id)
    report = container.last_unconfirmed_report()
    report.count += 1
    report.save()

    time.sleep(10)  # Ждём сохранения в БД

    """Если выполняются условия для вывоза по
    кол-ву бумаги, сообщаем"""
    if container.is_reported_just_enough():
        check_mass_condition_to_notify(container)


@shared_task
def handle_empty_container(container_id: int) -> None:
    """При опустошении контейнера нужно запомнить время
    и перечитать среднее время выноса"""
    container = Container.objects.get(pk=container_id)
    last_unconfirmed_report = container.last_unconfirmed_report()
    if last_unconfirmed_report:
        last_unconfirmed_report.emptied_at = timezone.now()
        last_unconfirmed_report.save()
        time.sleep(10)  # Ждём сохранения в БД
        calc_avg_takeout_wait_time(container)
