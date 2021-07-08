from django_filters import rest_framework as filters
from rest_framework import generics, permissions
from rest_framework.response import Response
from io import BytesIO
from django.core.files import File

from .models import Container, FullContainerReport
from .serializers import *
from .qr import generate_sticker


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


class ContainerDetailView(generics.RetrieveUpdateDestroyAPIView):
    """ View для CRUD-операций с контейнерами """
    serializer_class = ContainerSerializer
    queryset = Container.objects.all()


class ContainerListView(generics.ListCreateAPIView):
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


class BuildingListView(generics.ListAPIView):
    """Списко зданий (для опций при создании контейнера)"""
    serializer_class = BuildingSerializer
    queryset = Building.objects.all()


class GetStickerView(generics.RetrieveAPIView):
    """View для получения стикера контейнера"""
    queryset = Container.objects.all()
    serializer_class = ContainerStickerSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        if not instance.sticker:
            """Генерируем стикер, если его ещё нет."""
            sticker_im = generate_sticker(instance.pk)
            sticker_io = BytesIO()
            sticker_im.save(sticker_io, "JPEG", quality=85)
            sticker = File(sticker_io, name=f"sticker_{instance.pk}")
            instance.sticker = sticker
            instance.save()

        serializer = self.get_serializer(instance)
        return Response(serializer.data)
