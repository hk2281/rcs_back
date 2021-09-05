from django.http.response import HttpResponse
from django.utils import timezone
from rest_framework import views
from tempfile import NamedTemporaryFile

from .excel import *


class ContainerStatsExcelView(views.APIView):
    """Возвращает .xlsx файл со статистикой по контейнерам"""

    def get(self, request, *args, **kwargs):
        wb = get_container_stats_xl()
        with NamedTemporaryFile() as tmp:
            fname = "recycle-starter-container-stats-"
            fname += timezone.now().strftime("%d.%m.%Y")
            fname += ".xlsx"
            wb.save(tmp.name)
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
        wb = get_container_takeout_stats_xl()
        with NamedTemporaryFile() as tmp:
            fname = "recycle-starter-container-takeout-stats-"
            fname += timezone.now().strftime("%d.%m.%Y")
            fname += ".xlsx"
            wb.save(tmp.name)
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
        wb = get_tank_takeout_stats_xl()
        with NamedTemporaryFile() as tmp:
            fname = "recycle-starter-tank-takeout-stats-"
            fname += timezone.now().strftime("%d.%m.%Y")
            fname += ".xlsx"
            wb.save(tmp.name)
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
        wb = get_all_stats_xl()
        with NamedTemporaryFile() as tmp:
            fname = "recycle-starter-stats-"
            fname += timezone.now().strftime("%d.%m.%Y")
            fname += ".xlsx"
            wb.save(tmp.name)
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
