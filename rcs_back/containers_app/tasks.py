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
def container_add_report(container_id: int, by_staff: bool) -> None:
    container: Container = Container.objects.get(pk=container_id)
    container.add_report(by_staff)


@ shared_task
def handle_empty_container(container_id: int) -> None:
    """При опустошении контейнера нужно запомнить время
    и пересчитать среднее время выноса"""
    container: Container = Container.objects.get(pk=container_id)
    container.handle_empty()


@ shared_task
def container_correct_fullness(container_id: int) -> None:
    container: Container = Container.objects.get(pk=container_id)
    container.correct_fullness()
