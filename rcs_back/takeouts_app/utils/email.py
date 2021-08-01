from rcs_back.containers_app.models import Building, BuildingPart


def takeout_condition_met_notify(building: Building = None,
                                 building_part: BuildingPart = None) -> None:
    """Оповещение о необходимости сбора"""
    pass


def containers_takeout_notify():
    pass


def tank_takeout_notify():
    pass
