import time

from celery import shared_task

from rcs_back.containers_app.models import Container


@shared_task
def public_container_add_notify(container_id: int) -> None:
    """Отправляет сообщение с инструкциями для активации
    добавленного контейнера"""
    time.sleep(5)  # Ждём сохранения в БД
    container: Container = Container.objects.get(pk=container_id)
    container.public_add_notify()


@shared_task
def handle_first_full_report(container_id: int, by_staff: bool) -> None:
    """При заполнении контейнера нужно запомнить время
    и пересчитать среднее время заполнения"""
    container: Container = Container.objects.get(pk=container_id)
    container.handle_first_full_report(by_staff)


@shared_task
def handle_repeat_full_report(container_id: int, by_staff: bool) -> None:
    """При повторном сообщении о заполнении нужно
    увеличить кол-во сообщений"""
    container: Container = Container.objects.get(pk=container_id)
    container.handle_repeat_full_report(by_staff)


@shared_task
def handle_empty_container(container_id: int) -> None:
    """При опустошении контейнера нужно запомнить время
    и пересчитать среднее время выноса"""
    container: Container = Container.objects.get(pk=container_id)
    container.handle_empty()


@shared_task
def container_correct_fullness(container_id: int) -> None:
    container: Container = Container.objects.get(pk=container_id)
    container.correct_fullness()
