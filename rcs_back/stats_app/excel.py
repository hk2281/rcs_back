from datetime import timedelta
from django.db.models.query import QuerySet
from openpyxl import Workbook
from openpyxl.styles import Font
from openpyxl.worksheet.worksheet import Worksheet

from rcs_back.containers_app.models import Container, Building
from rcs_back.takeouts_app.models import (ContainersTakeoutRequest,
                                          TankTakeoutRequest)


def queryset_to_ids(qs: QuerySet) -> str:
    """Форматирование QuerySet"""
    s = ""
    for item in qs:
        s += str(item.pk)
        s += ", "
    return s[:len(s)-2]


def format_td(td: timedelta) -> str:
    """Форматирование timedelta"""
    td_s = str(td)
    if "day" in td_s:
        td_s = td_s.split(":")[0]
        days = td_s[:td_s.find(" ")]
        hours = td_s[td_s.find(",") + 2:]
        return f"{days} дн {hours} ч"
    else:
        return td_s.split(":")[0] + " ч"


def set_width(ws: Worksheet) -> None:
    """Ширина столбца как наибольшая из клеток"""
    dims = {}
    for row in ws.rows:
        for cell in row:
            if cell.value:
                dims[cell.column_letter] = max(
                    (dims.get(cell.column_letter, 0),
                     len(str(cell.value)))
                ) + 0.5
    for col, value in dims.items():
        ws.column_dimensions[col].width = value


def write_container_headers(ws: Worksheet) -> None:
    """Записывает заголовки в статистику о контейнере"""
    ws["A2"] = "ID"
    ws["B2"] = "Вид контейнера"
    ws["C2"] = "Масса, кг"
    ws["D2"] = "Адрес здания"
    ws["E2"] = "Номер корпуса"
    ws["F2"] = "Этаж"
    ws["G2"] = "Аудитория"
    ws["H2"] = "Описание"
    ws["I2"] = "Состояние"
    ws["J2"] = "Текущее"
    ws["K2"] = "Среднее"
    ws["L2"] = "Текущее"
    ws["M2"] = "Среднее"
    ws["N2"] = "Номер телефона"
    ws["O2"] = "Почта"
    ws["P2"] = "Суммарная масса, кг"
    ws["J1"] = "Время заполнения"
    ws["L1"] = "Ожидание сбора после заполнения"
    ws["N1"] = "Контактное лицо"

    ws.row_dimensions[1].font = Font(bold=True)
    ws.row_dimensions[2].font = Font(bold=True)


def write_container(c: Container, ws: Worksheet, i: int) -> None:
    """Записывает статистику одного контейнера"""
    ws[f"A{i}"] = c.pk
    ws[f"B{i}"] = c.get_kind_display()
    ws[f"C{i}"] = c.mass()
    ws[f"D{i}"] = c.building.address
    if c.building_part:
        ws[f"E{i}"] = c.building_part.num
    else:
        ws[f"E{i}"] = "-"
    ws[f"F{i}"] = c.floor
    ws[f"G{i}"] = c.room
    ws[f"H{i}"] = c.description
    ws[f"I{i}"] = c.get_status_display()
    if c.cur_fill_time():
        ws[f"J{i}"] = format_td(c.cur_fill_time())
    else:
        ws[f"J{i}"] = "Уже заполнен"
    if c.avg_fill_time:
        ws[f"K{i}"] = format_td(c.avg_fill_time)
    else:
        ws[f"K{i}"] = "Недостаточно данных"
    if c.cur_takeout_wait_time():
        ws[f"L{i}"] = format_td(c.cur_takeout_wait_time())
    else:
        ws[f"L{i}"] = "Ещё не заполнен"
    if c.avg_takeout_wait_time:
        ws[f"M{i}"] = format_td(c.avg_takeout_wait_time)
    else:
        ws[f"M{i}"] = "Недостаточно данных"
    ws[f"N{i}"] = c.phone
    ws[f"O{i}"] = c.email
    ws[f"P{i}"] = c.collected_mass()


def get_container_stats_ws(ws) -> None:
    """Создаёт страницу из excel с актуальной статистикой по контейнерам"""
    ws.title = "Контейнеры"
    write_container_headers(ws)
    containers = Container.objects.order_by("pk")

    for i in range(3, len(containers) + 3):
        container = containers[i-3]
        write_container(container, ws, i)

    set_width(ws)


def get_container_stats_xl() -> Workbook:
    """Создаёт excel-WorkBook с актуальной статистикой по контейнерам"""
    wb = Workbook()
    ws = wb.active
    get_container_stats_ws(ws)
    return wb


def write_container_takeout_headers(ws: Worksheet) -> None:
    """Записывает заголовки в статистику о сборе"""
    ws["A1"] = "Дата сбора"
    ws["A2"] = "создание"
    ws["B2"] = "подтверждение"
    ws["C1"] = "Здание"
    ws["D1"] = "Корпус"
    ws["E1"] = "Список контейнеров на сбор"
    ws["F1"] = "Неподтверждённые контейнеры"
    ws["G1"] = "Соответствие"
    ws["H1"] = "Суммарная масса сбора"
    ws["I1"] = "Данные подсобного рабочего"

    ws.row_dimensions[1].font = Font(bold=True)
    ws.row_dimensions[2].font = Font(bold=True)


def write_container_takeout(t: ContainersTakeoutRequest,
                            ws: Worksheet, i: int) -> None:
    """Записывает статистику одного сбора"""
    ws[f"A{i}"] = t.created_at.strftime("%d.%m.%Y")
    if t.confirmed_at:
        ws[f"B{i}"] = t.confirmed_at.strftime("%d.%m.%Y")
    else:
        ws[f"B{i}"] = "-"
    ws[f"C{i}"] = t.building.address
    if t.building_part:
        ws[f"D{i}"] = t.building_part.num
    else:
        ws[f"D{i}"] = "-"
    ws[f"E{i}"] = queryset_to_ids(t.containers.all())
    ws[f"F{i}"] = queryset_to_ids(t.unconfirmed_containers())
    ws[f"G{i}"] = t.emptied_containers_match()
    ws[f"H{i}"] = t.mass()
    ws[f"I{i}"] = t.worker_info


def get_container_takeout_stats_ws(ws) -> None:
    """Создаёт страницу из excel с актуальной статистикой по сборам"""
    ws.title = "Сборы"
    write_container_takeout_headers(ws)
    container_takeouts = ContainersTakeoutRequest.objects.order_by(
        "pk")

    for i in range(3, len(container_takeouts) + 3):
        takeout = container_takeouts[i-3]
        write_container_takeout(takeout, ws, i)

    set_width(ws)


def get_container_takeout_stats_xl() -> Workbook:
    """Создаёт excel-WorkBook с актуальной статистикой по сборам"""
    wb = Workbook()
    ws = wb.active
    get_container_takeout_stats_ws(ws)
    return wb


def write_tank_takeout_headers(ws: Worksheet) -> None:
    """Записывает заголовки в статистику о вывозе"""
    ws["A1"] = "Дата обращения к оператору"
    ws["B1"] = "Дата вывоза"
    ws["C1"] = "Здание"
    ws["D1"] = "Время заполнения накопительного бака"
    ws["E1"] = "Расчётная масса вывоза, кг"
    ws["F1"] = "Подтверждённая масса вывоза, кг"
    ws["G1"] = "Соответствие (расчётная/подтверждённая"
    ws["H1"] = "Разница (расчётная - подтверждённая), кг"

    ws.row_dimensions[1].font = Font(bold=True)


def write_tank_takeout(t: TankTakeoutRequest,
                       ws: Worksheet, i: int) -> None:
    """Записывает статистику одного вывоза"""
    ws[f"A{i}"] = t.created_at.strftime("%d.%m.%Y")
    if t.confirmed_at:
        ws[f"B{i}"] = t.confirmed_at.strftime("%d.%m.%Y")
    else:
        ws[f"B{i}"] = "-"
    ws[f"C{i}"] = t.building.address
    if t.fill_time():
        ws[f"D{i}"] = format_td(t.fill_time())
    else:
        ws[f"D{i}"] = "Недостаточно данных"
    ws[f"E{i}"] = t.mass()
    ws[f"F{i}"] = t.confirmed_mass
    ws[f"G{i}"] = t.confirmed_mass_match()
    ws[f"H{i}"] = t.mass_difference()


def get_tank_takeout_stats_ws(ws) -> None:
    """Создаёт страницу из excel с актуальной статистикой по вывозам"""
    ws.title = "Вывозы"
    write_tank_takeout_headers(ws)
    tank_takeouts = TankTakeoutRequest.objects.order_by(
        "pk")

    for i in range(2, len(tank_takeouts) + 2):
        takeout = tank_takeouts[i-2]
        write_tank_takeout(takeout, ws, i)

    set_width(ws)


def write_building_headers(ws: Worksheet) -> None:
    """Записывает заголовки в статистику по зданию"""
    ws["A1"] = "Здание"
    ws["B1"] = "Число контейнеров"
    ws["C1"] = "Суммарный объём, кг"
    ws["D1"] = "Средняя скорость сбора, кг/месяц"

    ws.row_dimensions[1].font = Font(bold=True)


def write_building(b: Building, ws: Worksheet, i: int) -> None:
    """Записывает статистику одного здания"""
    ws[f"A{i}"] = b.address
    ws[f"B{i}"] = b.container_count()
    ws[f"C{i}"] = b.confirmed_collected_mass()
    ws[f"D{i}"] = b.avg_fill_speed()


def get_building_stats_ws(ws) -> None:
    """Создаёт страницу из excel с актуальной статистикой по зданию"""
    ws.title = "По зданиям"
    write_building_headers(ws)
    buildings = Building.objects.order_by("pk")

    for i in range(2, len(buildings) + 2):
        building = buildings[i-2]
        write_building(building, ws, i)

    set_width(ws)


def get_tank_takeout_stats_xl() -> Workbook:
    """Создаёт excel-WorkBook с актуальной статистикой по вывозам"""
    wb = Workbook()
    ws = wb.active
    get_tank_takeout_stats_ws(ws)
    ws1 = wb.create_sheet()
    get_building_stats_ws(ws1)
    return wb


def get_all_stats_xl() -> Workbook:
    """Создаёт excel-WorkBook со всей актуальной статистикой"""
    wb = Workbook()
    ws = wb.active
    get_container_stats_ws(ws)
    ws1 = wb.create_sheet()
    get_container_takeout_stats_ws(ws1)
    ws2 = wb.create_sheet()
    get_tank_takeout_stats_ws(ws2)
    ws3 = wb.create_sheet()
    get_building_stats_ws(ws3)
    return wb
