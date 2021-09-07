from django.db.models import Q
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.http.response import HttpResponseRedirect
from rest_framework import (generics, views, permissions,
                            status as drf_status, exceptions)
from rest_framework.response import Response

from rcs_back.utils.mixins import UpdateThenRetrieveModelMixin
from rcs_back.takeouts_app.models import *
from rcs_back.takeouts_app.serializers import *
from rcs_back.takeouts_app.utils import *
from rcs_back.containers_app.models import Building, EmailToken
from rcs_back.containers_app.tasks import handle_empty_container
from rcs_back.containers_app.utils.model import total_mass


class ContainersTakeoutListView(generics.ListCreateAPIView):
    """CR для заявки на вынос контейнеров"""
    serializer_class = ContainersTakeoutRequestSerializer
    queryset = ContainersTakeoutRequest.objects.all()
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        if ("token" in request.query_params and
                "building" in request.query_params):
            """Создание сбора через письмо"""
            r_token = self.request.query_params.get("token")
            r_building = self.request.query_params.get("building")
            token = EmailToken.objects.filter(
                token=r_token
            ).first()
            building = get_object_or_404(Building, pk=r_building)
            if token:
                takeout = ContainersTakeoutRequest.objects.create(
                    building=building
                )
                takeout.containers.add(*building.containers_for_takeout())
                token.delete()
                title = "Создание сбора"
                text = "Сбор успешно создан"
                status = "success"
            else:
                title = "Ошибка активации"
                text = "Неверный токен для активации"
                status = "error"
            redirect_path = f"/reslult?title={title}&text={text}&status={status}"
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


class ContainersTakeoutConfirmationView(generics.UpdateAPIView):
    """View для создания подтверждения выноса контейнеров"""
    serializer_class = ContainersTakeoutConfirmationSerializer
    queryset = ContainersTakeoutRequest.objects.filter(
        confirmed_at__isnull=True
    )

    def perform_update(self, serializer):
        """PATCH-запрос должен использоваться только для подтверждения
        сбора"""
        serializer.save(confirmed_at=timezone.now())
        if "emptied_containers" in serializer.validated_data:
            emptied_containers = serializer.validated_data["emptied_containers"]
            for container in emptied_containers:
                handle_empty_container.delay(container.pk)


class TankTakeoutRequestListView(generics.ListCreateAPIView):
    serializer_class = TankTakeoutRequestSerializer
    queryset = TankTakeoutRequest.objects.all()

    def perform_create(self, serializer):
        instance = serializer.save()
        tank_takeout_notify(instance.building)


class TankTakeoutConfirmationView(generics.UpdateAPIView):
    """View для создания подтверждения вывоза бака"""
    serializer_class = TankTakeoutConfirmationSerializer
    queryset = TankTakeoutRequest.objects.filter(
        confirmed_at__isnull=True
    )

    def perform_update(self, serializer):
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
        for building in Building.objects.all():
            building_dict = {}
            building_dict[
                "collected_mass"] = building.confirmed_collected_mass()
            building_dict["container_count"] = building.container_count()
            resp[str(building)] = building_dict
        resp["total_mass"] = total_mass()
        return Response(resp)
