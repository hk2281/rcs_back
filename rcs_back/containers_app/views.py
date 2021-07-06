from django_filters import rest_framework as filters
from rest_framework import generics, permissions

from .models import Container, FullContainerReport
from .serializers import *


class FillContainerView(generics.UpdateAPIView):
    """ View для заполнения контейнера """
    permission_classes = [permissions.AllowAny]
    serializer_class = FillContainerSerializer
    queryset = Container.objects.filter(is_active=True)

    def perform_update(self, serializer) -> None:
        instance = self.get_object()
        if instance.is_full:
            full_container_report = FullContainerReport.objects.order_by(
                "-created_at"
            )[0]
            full_container_report.count += 1
            full_container_report.save()
        serializer.save()


class ContainerView(generics.RetrieveUpdateDestroyAPIView):
    """ View для CRUD-операций с контейнерами """
    serializer_class = ContainerSerializer
    queryset = Container.objects.all()
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = [
        "building",
        "building_part",
        "floor",
        "is_full",
        "is_active"
    ]
