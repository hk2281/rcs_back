import datetime
import time

from django.core.cache import cache
from django.core.mail import send_mail
from celery import shared_task

from rcs_back.containers_app.models import FullContainerReport, Container
from rcs_back.containers_app.utils.email import get_public_container_add_msg


@shared_task
def calc_avg_fill_time(container_pk: int) -> str:
    """Считаем среднее время заполнения контейнера"""
    time.sleep(10)  # Ждём сохранения в БД
    reports = FullContainerReport.objects.filter(
        container_id=container_pk
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
        cache.set(f"{container_pk}_avg_fill_time", avg_fill_time, None)
        return f"container {container_pk}: {avg_fill_time}"
    else:
        return "Контейнер заполнился только первый раз"


@shared_task
def calc_avg_takeout_wait_time(container_pk: int) -> str:
    """Считаем среднее время ожидания выноса контейнера"""
    time.sleep(10)  # Ждём сохранения в БД
    reports = FullContainerReport.objects.filter(
        container_id=container_pk
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
        cache.set(f"{container_pk}_avg_takeout_wait_time",
                  avg_takeout_wait_time, None)
        return f"container {container_pk}: {avg_takeout_wait_time}"


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
