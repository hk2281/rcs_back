from django.utils import timezone

from rcs_back.containers_app.models import Container, FullContainerReport
from rcs_back.containers_app.tasks import *


def check_takeout_condition():
    # TODO
    pass


def takeout_condition_met_notify():
    # TODO
    pass


def handle_full_container(container: Container) -> None:
    """При заполнении контейнера нужно запомнить время
    и пересчитать среднее время заполнения"""
    FullContainerReport.objects.create(
        container=container
    )
    calc_avg_fill_time.delay(container.pk)
    """Если выполняются условия для вывоза по
    кол-ву бумаги, сообщаем"""
    if check_takeout_condition():
        takeout_condition_met_notify()


def handle_empty_container(container: Container) -> None:
    """При опустошении контейнера нужно запомнить время
    и перечитать среднее время выноса"""
    last_full_report = container.last_full_report()
    if last_full_report:
        last_full_report.emptied_at = timezone.now()
        last_full_report.save()
        calc_avg_takeout_wait_time.delay(container.pk)
