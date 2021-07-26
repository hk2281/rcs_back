from django.utils import timezone
from rest_framework import generics, views
from rest_framework.response import Response

from rcs_back.takeouts_app.models import *
from rcs_back.takeouts_app.serializers import *
from rcs_back.takeouts_app.utils import *
from rcs_back.containers_app.view_utils import handle_empty_container


class ContainersTakeoutListView(generics.ListCreateAPIView):
    """CR для заявки на вынос контейнеров"""
    serializer_class = ContainersTakeoutRequestSerializer
    queryset = ContainersTakeoutRequest.objects.all()

    def perform_create(self, serializer):
        serializer.save()
        containers_takeout_notify()


class ContainersTakeoutConfirmationView(generics.UpdateAPIView):
    """View для создания подтверждения выноса контейнеров"""
    serializer_class = ContainersTakeoutConfirmationSerializer
    queryset = ContainersTakeoutRequest.objects.filter(
        confirmed_at__isnull=True
    )

    def perform_update(self, serializer):
        serializer.save(confirmed_at=timezone.now())
        emptied_containers = serializer.validated_data["emptied_containers"]
        for container in emptied_containers:
            """Меняем статус контейнера и
            фиксируем время подтверждения выноса"""
            container.is_full = False
            container.save()
            handle_empty_container(container)


class TankTakeoutRequestListView(generics.ListCreateAPIView):
    serializer_class = TankTakeoutRequestSerializer
    queryset = TankTakeoutRequest.objects.all()

    def perform_create(self, serializer):
        serializer.save()
        tank_takeout_notify()


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
    filterset_fields = ["building", "building_part"]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return AddTakeoutConditionSerializer
        else:
            return TakeoutConditionSerializer


class TakeoutConditionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = TakeoutCondition.objects.all()

    def get_serializer_class(self):
        if self.request.method == "GET":
            return TakeoutConditionSerializer
        else:
            return AddTakeoutConditionSerializer


class TakeoutConditionTypeOptionsView(views.APIView):
    """Типы условий для сбора"""
    types = {
        1: "не больше N дней в офисе",
        2: "не больше N дней в общественном месте",
        3: "суммарная масса бумаги в корпусе не больше N кг",
        4: ("игнорировать первые N сообщений "
            "о заполненности контейнера в общественном месте")
    }

    def get(self, request, *args, **kwargs):
        return Response(self.types)
