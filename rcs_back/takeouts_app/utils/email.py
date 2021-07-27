from rcs_back.containers_app.models import Building, BuildingPart


def takeout_condition_met_notify(building: Building,
                                 building_part: BuildingPart) -> None:
    """Оповещение о необходимости сбора"""
    pass


def containers_takeout_notify():
    pass


def tank_takeout_notify():
    pass
