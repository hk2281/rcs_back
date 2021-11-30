import datetime
from tempfile import NamedTemporaryFile

from django.http.response import HttpResponse
from django.utils import timezone
from rest_framework import permissions, views
from rest_framework.response import Response

from rcs_back.containers_app.models import Building

from .excel import (
    get_all_stats_xl,
    get_container_stats_xl,
    get_container_takeout_stats_xl,
    get_tank_takeout_stats_xl,
)


class ContainerStatsExcelView(views.APIView):
    """Возвращает .xlsx файл со статистикой по контейнерам"""

    def get(self, request, *args, **kwargs):
        workbook = get_container_stats_xl()
        with NamedTemporaryFile() as tmp:
            fname = "recycle-starter-container-stats-"
            fname += timezone.now().strftime("%d.%m.%Y")
            fname += ".xlsx"
            workbook.save(tmp.name)
            file_data = tmp.read()
            response = HttpResponse(
                file_data,
                headers={
                    "Content-Type": "application/vnd.ms-excel",
                    "Content-Disposition":
                    f'attachment; filename={fname}',
                    "Content-Language": "ru-RU"
                }
            )
            return response


class ContainerTakeoutStatsExcelView(views.APIView):
    """Возвращает .xlsx файл со статистикой по сборам"""

    def get(self, request, *args, **kwargs):
        workbook = get_container_takeout_stats_xl()
        with NamedTemporaryFile() as tmp:
            fname = "recycle-starter-container-takeout-stats-"
            fname += timezone.now().strftime("%d.%m.%Y")
            fname += ".xlsx"
            workbook.save(tmp.name)
            file_data = tmp.read()
            response = HttpResponse(
                file_data,
                headers={
                    "Content-Type": "application/vnd.ms-excel",
                    "Content-Disposition":
                    f'attachment; filename={fname}',
                    "Content-Language": "ru-RU"
                }
            )
            return response


class TankTakeoutStatsExcelView(views.APIView):
    """Возвращает .xlsx файл со статистикой по сборам"""

    def get(self, request, *args, **kwargs):
        workbook = get_tank_takeout_stats_xl()
        with NamedTemporaryFile() as tmp:
            fname = "recycle-starter-tank-takeout-stats-"
            fname += timezone.now().strftime("%d.%m.%Y")
            fname += ".xlsx"
            workbook.save(tmp.name)
            file_data = tmp.read()
            response = HttpResponse(
                file_data,
                headers={
                    "Content-Type": "application/vnd.ms-excel",
                    "Content-Disposition":
                    f'attachment; filename={fname}',
                    "Content-Language": "ru-RU"
                }
            )
            return response


class AllStatsExcelView(views.APIView):
    """Возвращает .xlsx файл со статистикой по сборам"""

    def get(self, request, *args, **kwargs):
        workbook = get_all_stats_xl()
        with NamedTemporaryFile() as tmp:
            fname = "recycle-starter-stats-"
            fname += timezone.now().strftime("%d.%m.%Y")
            fname += ".xlsx"
            workbook.save(tmp.name)
            file_data = tmp.read()
            response = HttpResponse(
                file_data,
                headers={
                    "Content-Type": "application/vnd.ms-excel",
                    "Content-Disposition":
                    f'attachment; filename={fname}',
                    "Content-Language": "ru-RU"
                }
            )
            return response


# Дата запуска сервиса в прод
START_DATE = datetime.date(day=1, month=10, year=2021)


class MonthlyMassPerBuildingView(views.APIView):
    """Масса макулатуры, подтверждённой после вывозов баков,
    за каждый месяц. Параметр year выбирает, за какой год"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        resp = []
        today = timezone.now().date()
        current_year: int = today.year
        current_month: int = today.month

        year = int(request.query_params.get("year"))
        if year < 2021 or year > current_year:
            return Response(resp)

        if year == 2021:
            start_month = START_DATE.month
        else:
            start_month = 1

        if year == current_year:
            end_month = current_month
        else:
            end_month = 12

        building: Building
        for building in Building.objects.all():
            building_dict = {}
            building_dict["id"] = building.pk
            building_dict["address"] = building.address

            current_month = start_month
            months = []
            while current_month <= end_month:
                month_dict = {}
                month_dict["month"] = current_month
                month_dict["mass"] = building.confirmed_collected_mass(
                    start_date=datetime.date(year=year, month=current_month, day=1)
                )
                current_month += 1
                months.append(month_dict)

            building_dict["collected_mass"] = months
            resp.append(building_dict)
        return Response(resp)


class YearlyMassPerBuildingView(views.APIView):
    """Масса макулатуры, подтверждённой после вывозов баков,
    за каждый год"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        resp = []

        building: Building
        for building in Building.objects.all():
            building_dict = {}
            building_dict["id"] = building.pk
            building_dict["address"] = building.address

            current_year = START_DATE.year
            end_year = timezone.now().date().year
            years = []
            while current_year <= end_year:
                year_dict = {}
                year_dict["year"] = current_year
                year_dict["mass"] = building.confirmed_collected_mass(
                    start_date=datetime.date(year=current_year, month=1, day=1),
                    yearly=True
                )
                current_year += 1
                years.append(year_dict)

            building_dict["collected_mass"] = years
            resp.append(building_dict)
        return Response(resp)


class MonthlyActivationsPerBuildingView(views.APIView):
    """Кол-во контейнеров, подключенных к сервису,
    за каждый месяц. Параметр year выбирает, за какой год"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        resp = []
        today = timezone.now().date()
        current_year: int = today.year
        current_month: int = today.month

        year = int(request.query_params.get("year"))
        if year < 2021 or year > current_year:
            return Response(resp)

        if year == 2021:
            start_month = START_DATE.month
        else:
            start_month = 1

        if year == current_year:
            end_month = current_month
        else:
            end_month = 12

        building: Building
        for building in Building.objects.all():
            building_dict = {}
            building_dict["id"] = building.pk
            building_dict["address"] = building.address

            current_month = start_month
            months = []
            while current_month <= end_month:
                month_dict = {}
                month_dict["month"] = current_month
                month_dict["activations"] = building.activated_containers(
                    datetime.date(year=year, month=current_month, day=1)
                )
                current_month += 1
                months.append(month_dict)

            building_dict["activations"] = months
            resp.append(building_dict)
        return Response(resp)
