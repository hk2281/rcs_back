from rcs_back.containers_app.models import Building


def total_mass() -> int:
    """Сумма собранной макулатуры по всем зданиям"""
    mass = 0
    for building in Building.objects.all():
        mass += building.confirmed_collected_mass()
    return mass
