from celery import shared_task

from rcs_back.containers_app.models import Building
from rcs_back.takeouts_app.utils.email import takeout_condition_met_notify


@shared_task
def check_time_conditions() -> str:
    '''Выполнены ли условия "не больше N дней"'''
    buildings = Building.objects.all()
    buildings_for_takeout = []
    building_parts_for_takeout = []
    for building in buildings:
        building_parts = building.building_parts.all()
        if building_parts:
            for building_part in building_parts:
                if building_part.needs_takeout():
                    takeout_condition_met_notify(building_part=building_part)
                    building_parts_for_takeout.append(building_part)
        else:
            if building.needs_takeout():
                takeout_condition_met_notify(building=building)
                buildings_for_takeout.append(building)
    res = ""
    if buildings_for_takeout:
        res += "Сбор необходим в зданиях: "
        for building in buildings_for_takeout:
            res += f"{building}, "
        res += "."
    if building_parts_for_takeout:
        res += "Сбор необходим в корпусах: "
        for part in building_parts_for_takeout:
            res += f"{part}, "
        res += "."
    if not res:
        res = "Сбор нигде не требуется"
    return res
