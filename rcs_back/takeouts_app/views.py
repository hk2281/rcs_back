import pandas as pd
import pdfkit

from django.conf import settings
from django.db.models import Q
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.http.response import HttpResponseRedirect, HttpResponse
from rest_framework import (generics, views, permissions,
                            status as drf_status, exceptions)
from rest_framework.response import Response
from tempfile import NamedTemporaryFile

from rcs_back.utils.mixins import UpdateThenRetrieveModelMixin
from rcs_back.takeouts_app.models import *
from rcs_back.takeouts_app.serializers import *
from rcs_back.containers_app.models import Building, EmailToken
from rcs_back.containers_app.tasks import handle_empty_container
from rcs_back.stats_app.excel import get_short_container_info_xl


class ContainersTakeoutListView(generics.ListCreateAPIView):
    """CR для заявки на вынос контейнеров"""
    serializer_class = ContainersTakeoutRequestSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = ContainersTakeoutRequest.objects.all()
        if (self.request.user.is_authenticated and
            self.request.user.groups.filter(
                name=settings.HOZ_GROUP) and
                self.request.user.building):
            queryset = queryset.filter(
                building=self.request.user.building
            )
        return queryset

    def get(self, request, *args, **kwargs):
        if ("token" in request.query_params and
                "building" in request.query_params):
            """Создание сбора через письмо"""
            r_token = self.request.query_params.get("token")
            r_building = self.request.query_params.get("building")
            token: EmailToken = EmailToken.objects.filter(
                token=r_token
            ).first()
            building = get_object_or_404(Building, pk=r_building)
            if token and not token.is_used:
                takeout = ContainersTakeoutRequest.objects.create(
                    building=building
                )
                takeout.containers.add(*building.containers_for_takeout())
                token.use()
                title = "Создание сбора"
                text = "Сбор успешно создан"
                status = "success"
            elif token:
                title = "Повторное создание"
                text = "Сбор уже был создан"
                status = "info"
            else:
                title = "Ошибка активации"
                text = "Неверный токен для активации"
                status = "error"
            redirect_path = f"/result?title={title}&text={text}"
            redirect_path += f"&status={status}"
            return HttpResponseRedirect(
                redirect_to=settings.DOMAIN + redirect_path
            )
        elif request.user.is_authenticated:
            """Получение списка сборов через сайт"""
            return self.list(request, *args, **kwargs)
        else:
            """Попытка выполнить метод GET без токена и авторизации"""
            raise exceptions.NotAuthenticated()

    def post(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            """Создание сбора через сайт"""
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            if "all-full-containers" in self.request.query_params:
                """Сбор всех полных контейнеров"""
                building = serializer.validated_data["building"]
                takeout = serializer.save()
                takeout.containers.add(*building.containers_for_takeout())
                headers = self.get_success_headers(serializer.data)
                return Response(
                    self.serializer_class(takeout).data,
                    status=drf_status.HTTP_201_CREATED,
                    headers=headers
                )
            else:
                """Обычное создание сбора"""
                serializer.save()
                headers = self.get_success_headers(serializer.data)
                return Response(
                    serializer.data, status=drf_status.HTTP_201_CREATED,
                    headers=headers
                )
        else:
            """Попытка создать сбора без авторизации"""
            raise exceptions.NotAuthenticated()


class ContainersTakeoutDetailView(generics.RetrieveUpdateAPIView):
    """View для создания подтверждения выноса контейнеров
    и для ретрива"""
    queryset = ContainersTakeoutRequest.objects.all()

    def get_serializer_class(self):
        if self.request.method == "PATCH":
            return ContainersTakeoutConfirmationSerializer
        else:
            return ContainersTakeoutRequestSerializer

    def perform_update(self, serializer):
        """PATCH-запрос должен использоваться только для подтверждения
        сбора"""

        takeout = self.get_object()
        if takeout.confirmed_at:
            raise exceptions.ValidationError(
                {"error": "Сбор уже подтверждён"}
            )

        serializer.save(confirmed_at=timezone.now())
        if "emptied_containers" in serializer.validated_data:
            emptied_containers = serializer.validated_data[
                "emptied_containers"
            ]
            for container in emptied_containers:
                handle_empty_container.delay(container.pk)
            building = self.get_object().building
            building._takeout_notified = False
            building.save()


class ContainersForTakeoutView(views.APIView):
    """View для получения PDF со списком
    контейнеров на сбор"""
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        """Чтобы сделать из excel pdf, нужно провести
        следующую цепочку:
        excel -> pandas -> html -> pdf"""
        takeout_pk = self.kwargs["pk"]
        takeout = get_object_or_404(
            ContainersTakeoutRequest,
            pk=int(takeout_pk)
        )
        containers = takeout.containers.all()
        wb = get_short_container_info_xl(containers)

        with NamedTemporaryFile() as xl_f, \
                NamedTemporaryFile(suffix=".html") as html_f, \
                NamedTemporaryFile(suffix=".pdf") as pdf_f:

            wb.save(xl_f.name)

            df = pd.read_excel(
                xl_f.name,
                na_filter=False  # Чтобы не было "NaN" в пустых клетках
            )

            html = df.to_html(index=False)  # чтобы не было столбца индекс
            with open(html_f.name, "w", encoding="utf-8") as file:
                # чтобы была правильная кодировка
                file.writelines('<meta charset="UTF-8">\n')
                file.write(html)

            pdfkit.from_file(html_f.name, pdf_f.name)

            fname = "recycle-starter-containers-takeout-"
            fname += timezone.now().strftime("%d.%m.%Y")
            fname += ".pdf"
            file_data = pdf_f

            response = HttpResponse(
                file_data,
                headers={
                    "Content-Type": "application/pdf",
                    "Content-Disposition":
                    f'attachment; filename={fname}'
                }
            )

            return response


class TankTakeoutRequestListView(generics.ListCreateAPIView):
    serializer_class = TankTakeoutRequestSerializer

    def get_queryset(self):
        queryset = TankTakeoutRequest.objects.all()
        if (self.request.user.is_authenticated and
            self.request.user.groups.filter(
                name=settings.HOZ_GROUP) and
                self.request.user.building):
            queryset = queryset.filter(
                building=self.request.user.building
            )
        return queryset

    def perform_create(self, serializer):
        instance = serializer.save()
        instance.building.tank_takeout_notify()


class TankTakeoutDetailView(generics.RetrieveUpdateAPIView):
    """View для создания подтверждения вывоза бака
    и для ретрива"""
    queryset = TankTakeoutRequest.objects.all()

    def get_serializer_class(self):
        if self.request.method == "PATCH":
            return TankTakeoutConfirmationSerializer
        else:
            return TankTakeoutRequestSerializer

    def perform_update(self, serializer):
        """PATCH-запрос должен использоваться только для подтверждения
        вывоза"""

        takeout = self.get_object()
        if takeout.confirmed_at:
            raise exceptions.ValidationError(
                {"error": "Вывоз уже подтверждён"}
            )

        serializer.save(confirmed_at=timezone.now())


class TakeoutConditionListView(generics.ListCreateAPIView):
    queryset = TakeoutCondition.objects.all()
    filterset_fields = ["building_part"]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return AddTakeoutConditionSerializer
        else:
            return TakeoutConditionSerializer

    def get_queryset(self):
        if "building" in self.request.query_params:
            building_pk = self.request.query_params.get("building")
            return TakeoutCondition.objects.filter(
                Q(building__pk=building_pk) |
                Q(building_part__building__pk=building_pk)
            )


class TakeoutConditionDetailView(UpdateThenRetrieveModelMixin,
                                 generics.RetrieveUpdateDestroyAPIView):
    queryset = TakeoutCondition.objects.all()
    retrieve_serializer = TakeoutConditionSerializer
    update_serializer = AddTakeoutConditionSerializer

    def get_serializer_class(self):
        if self.request.method == "GET":
            return self.retrieve_serializer
        else:
            return self.update_serializer


class CollectedMassView(views.APIView):
    """Статистика собранной массы макулатуры для главной страницы"""
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        resp = {}
        total_mass = 0
        for building in Building.objects.all():
            building_dict = {}
            building_dict[
                "collected_mass"] = building.confirmed_collected_mass()
            total_mass += building.confirmed_collected_mass()
            building_dict["container_count"] = building.container_count()
            resp[str(building)] = building_dict
        total_mass = total_mass // 1000  # В тоннах
        resp["total_mass"] = total_mass
        resp["trees"] = total_mass * 12
        resp["energy"] = total_mass * 4.7
        resp["water"] = total_mass * 33
        return Response(resp)
