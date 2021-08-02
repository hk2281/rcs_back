from django.utils import timezone

from rcs_back.containers_app.models import Container, FullContainerReport
from rcs_back.containers_app.tasks import *
from rcs_back.takeouts_app.utils.email import takeout_condition_met_notify


def handle_repeat_full_report(container: Container) -> None:
    """Проверяем, не нужно ли отправить оповещение для сбора контейнеров"""
    if (container.building_part and
            container.building_part.meets_mass_takeout_condition()):
        takeout_condition_met_notify(
            "mass", building_part=container.building_part)
    elif container.building.meets_mass_takeout_condition():
        takeout_condition_met_notify("mass", building=container.building)


def handle_first_full_report(container: Container) -> None:
    """При заполнении контейнера нужно запомнить время
    и пересчитать среднее время заполнения"""
    FullContainerReport.objects.create(
        container=container
    )
    calc_avg_fill_time.delay(container.pk)
    """Если выполняются условия для вывоза по
    кол-ву бумаги, сообщаем"""
    handle_repeat_full_report(container)


def handle_empty_container(container: Container) -> None:
    """При опустошении контейнера нужно запомнить время
    и перечитать среднее время выноса"""
    last_full_report = container.last_full_report()
    if last_full_report:
        last_full_report.emptied_at = timezone.now()
        last_full_report.save()
        calc_avg_takeout_wait_time.delay(container.pk)
