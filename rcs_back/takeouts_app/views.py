from django.utils import timezone
from rest_framework import generics

from rcs_back.takeouts_app.models import *
from rcs_back.takeouts_app.serializers import *
from rcs_back.containers_app.tasks import calc_avg_takeout_wait_time


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
            last_full_report = container.last_full_report()
            if last_full_report:
                last_full_report.emptied_at = timezone.now()
                last_full_report.save()
                calc_avg_takeout_wait_time.delay(container.pk)
            # FIXME продублировать эту логику
