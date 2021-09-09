from celery import shared_task

from rcs_back.containers_app.models import Building


@shared_task
def check_time_conditions() -> None:
    '''Выполнены ли условия "не больше N дней"'''
    for building in Building.objects.all():
        building.check_conditions_to_notify()
