from datetime import timedelta

import pdfkit
from django.conf import settings
from django.db.models import Q, Sum
from django.db.models.functions import Coalesce
from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils import timezone
from rest_framework import exceptions, generics, permissions, serializers
from rest_framework import status as drf_status
from rest_framework import views
from rest_framework.response import Response

from rcs_back.containers_app.models import Building, EmailToken
from rcs_back.containers_app.tasks import (
    container_correct_fullness,
    handle_empty_container,
)
from rcs_back.takeouts_app.models import (
    ContainersTakeoutRequest,
    TakeoutCondition,
    TankTakeoutRequest,
)
from rcs_back.takeouts_app.serializers import (
    AddContainersTakeoutSerializer,
    AddTakeoutConditionSerializer,
    ArchiveTakeoutSerializer,
    ContainersTakeoutConfirmationSerializer,
    TakeoutConditionSerializer,
    TankTakeoutConfirmationSerializer,
    TankTakeoutRequestSerializer,
)
from rcs_back.utils.mixins import UpdateThenRetrieveModelMixin


class ContainersTakeoutListView(generics.ListCreateAPIView):
    """CR для заявки на вынос контейнеров"""
    serializer_class = AddContainersTakeoutSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = ContainersTakeoutRequest.objects.all()
        if (
            self.request.user.is_authenticated
            and
            self.request.user.groups.filter(name=settings.HOZ_GROUP).exists()
            and
            self.request.user.building.exists()
        ):
            queryset = queryset.filter(building__in=self.request.user.building.all())

        three_months_ago = timezone.now() - timedelta(days=3*30)
        queryset = queryset.filter(
            created_at__gt=three_months_ago
        )
        return queryset

    def get(self, request, *args, **kwargs):
        if ("token" in request.query_params and
                "building" in request.query_params):
            # Создание сбора через письмо
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
                redirect_to="https://" + settings.DOMAIN + redirect_path
            )
        elif request.user.is_authenticated:
            # Получение списка сборов через сайт
            return self.list(request, *args, **kwargs)
        else:
            # Попытка выполнить метод GET без токена и авторизации
            raise exceptions.NotAuthenticated()

    def post(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            # Создание сбора через сайт
            serializer = AddContainersTakeoutSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            if "all-full-containers" in self.request.query_params:
                # Сбор всех полных контейнеров
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
                # Обычное создание сбора
                serializer.save()
                headers = self.get_success_headers(serializer.data)
                return Response(
                    serializer.data, status=drf_status.HTTP_201_CREATED,
                    headers=headers
                )
        else:
            # Попытка создать сбора без авторизации
            if "archive_room" in request.data:
                # Можно создать сбор архива без авторизации
                serializer = ArchiveTakeoutSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                headers = self.get_success_headers(serializer.data)
                return Response(
                    serializer.data, status=drf_status.HTTP_201_CREATED,
                    headers=headers
                )
            else:
                # Обычный сбор создать без авторизации нельзя
                raise exceptions.NotAuthenticated()


class ContainersTakeoutDetailView(generics.RetrieveUpdateAPIView):
    """View для создания подтверждения выноса контейнеров
    и для ретрива"""
    queryset = ContainersTakeoutRequest.objects.all()
    serializer_class = ContainersTakeoutConfirmationSerializer

    def perform_update(self, serializer):
        """PATCH-запрос должен использоваться только для подтверждения
        сбора"""

        takeout: ContainersTakeoutRequest = self.get_object()
        if takeout.confirmed_at:
            raise exceptions.ValidationError(
                {"error": "Сбор уже подтверждён"}
            )

        if "emptied_containers" in serializer.validated_data:
            emptied_containers = serializer.validated_data[
                "emptied_containers"
            ]

        else:
            emptied_containers = set(list(takeout.containers.all()))
            if "already_empty_containers" in serializer.validated_data:
                already_empty_containers = set(serializer.validated_data[
                    "already_empty_containers"
                ])
                emptied_containers -= already_empty_containers

                for container in already_empty_containers:
                    container_correct_fullness.delay(container.pk)

            if "unavailable_containers" in serializer.validated_data:
                unavailable_containers = set(serializer.validated_data[
                    "unavailable_containers"
                ])
                emptied_containers -= unavailable_containers

        for container in emptied_containers:
            handle_empty_container.delay(container.pk)

        serializer.save(
            confirmed_at=timezone.now(),
            emptied_containers=emptied_containers
        )

        if not takeout.archive_mass and not takeout.archive_room:
            building: Building = takeout.building
            building._takeout_notified = False  # pylint: disable=protected-access
            building.save()


class ContainersForTakeoutView(views.APIView):
    """View для получения PDF со списком
    контейнеров на сбор"""

    def get(self, request, *args, **kwargs):
        takeout_pk = self.kwargs["pk"]
        takeout = get_object_or_404(
            ContainersTakeoutRequest,
            pk=int(takeout_pk)
        )
        containers_html_s = render_to_string(
            "containers_for_takeout.html", {
                "containers": takeout.containers.all(),
                "has_building_parts": True,
            }
        )
        pdf = pdfkit.from_string(containers_html_s, False)

        response = HttpResponse(
            pdf,
            headers={
                "Content-Type": "application/pdf",
                "Content-Disposition":
                    'attachment; filename=containers.pdf'
            }
        )

        return response


class TankTakeoutRequestListView(generics.ListCreateAPIView):
    serializer_class = TankTakeoutRequestSerializer

    def get_queryset(self):
        queryset = TankTakeoutRequest.objects.all()
        if (
            self.request.user.is_authenticated and
            self.request.user.groups.filter(name=settings.HOZ_GROUP).exists() and
            self.request.user.building.exists()
        ):
            queryset = queryset.filter(building__in=self.request.user.building.all())

        three_months_ago = timezone.now() - timedelta(days=3*30)
        queryset = queryset.filter(
            created_at__gt=three_months_ago
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
        else:
            raise serializers.ValidationError("Specify building")


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

        collected_mass = TankTakeoutRequest.objects.filter(
            confirmed_mass__isnull=False
        ).aggregate(
            collected_mass=Coalesce(Sum("confirmed_mass"), 0)
        )["collected_mass"]

        precollected_mass = Building.objects.filter(
            precollected_mass__isnull=False
        ).aggregate(
            precollected_mass=Coalesce(Sum("precollected_mass"), 0)
        )["precollected_mass"]

        total_mass = (collected_mass +
                      precollected_mass) // 100 / 10  # В тоннах до десятых
        resp["total_mass"] = total_mass

        resp["trees"] = int(total_mass * 12)
        resp["energy"] = int(total_mass * 4.7)
        resp["water"] = int(total_mass * 33)
        return Response(resp)
