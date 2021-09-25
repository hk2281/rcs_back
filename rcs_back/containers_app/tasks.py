import time

from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils import timezone
from celery import shared_task
from tempfile import NamedTemporaryFile

from rcs_back.containers_app.models import FullContainerReport, Container
from rcs_back.containers_app.utils.qr import generate_sticker


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
        "Добавление контейнера в сервисе RecycleStarter",
        msg,
        None,
        [container.email]
    )
    email.content_subtype = "html"
    with NamedTemporaryFile() as tmp:
        sticker_im = generate_sticker(container_id)
        sticker_im.save(tmp.name, "pdf", quality=100)
        email.attach("sticker.png", tmp.read(), "application/pdf")
        email.send()


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
    кол-ву бумаги, нужно сообщить"""
    container.check_fullness()


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
    container.check_fullness()


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
