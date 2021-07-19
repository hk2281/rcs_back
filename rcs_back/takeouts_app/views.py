from django.utils import timezone
from rest_framework import generics

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
