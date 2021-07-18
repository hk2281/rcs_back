from rest_framework import generics

from rcs_back.takeouts_app.models import *
from rcs_back.takeouts_app.serializers import *
from rcs_back.containers_app.view_utils import handle_empty_container


class ContainersTakeoutListView(generics.ListCreateAPIView):
    """CRUD для заявки на вынос контейнеров"""
    serializer_class = ContainersTakeoutRequestSerializer
    queryset = ContainersTakeoutRequest.objects.all()


class ContainersTakeoutConfirmationListView(generics.CreateAPIView):
    """View для создания подтверждения выноса контейнеров"""
    serializer_class = ContainersTakeoutConfirmationSerializer
    queryset = ContainersTakeoutConfirmation.objects.all()

    def perform_create(self, serializer):
        serializer.save()
        containers = serializer.validated_data["containers"]
        for container in containers:
            """Меняем статус контейнера и
            фиксируем время подтверждения выноса"""
            container.is_full = False
            container.save()
            handle_empty_container(container)


class TankTakeoutRequestListView(generics.ListCreateAPIView):
    serializer_class = TankTakeoutRequestSerializer
    queryset = TankTakeoutRequest.objects.all()
