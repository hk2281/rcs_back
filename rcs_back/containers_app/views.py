from django_filters import rest_framework as filters
from rest_framework import generics, permissions
from rest_framework.response import Response
from io import BytesIO
from django.core.files import File

from rcs_back.containers_app.models import Container, FullContainerReport
from .serializers import *
from .qr import generate_sticker
from .tasks import calc_avg_fill_time


class FillContainerView(generics.UpdateAPIView):
    """ View для заполнения контейнера """
    permission_classes = [permissions.AllowAny]
    serializer_class = FillContainerSerializer
    queryset = Container.objects.filter(is_active=True)

    def perform_update(self, serializer) -> None:
        instance = self.get_object()
        if instance.is_full:
            # Повторное сообщение
            instance.last_full_report().count += 1
            instance.last_full_report().save()
        else:
            # FIXME: продублировать в update
            FullContainerReport.objects.create(
                container=instance
            )
            calc_avg_fill_time.delay(instance.pk)
            """Если в здании достаточно полных контейнеров,
            сообщаем"""
            # FIXME: новые условия отбора
            # if not self.building.is_full:
            #     is_building_full = self.building.check_full_count()
            #     if is_building_full:
            #         self.building.is_full = True
            #         self.building.save()
            #         self.building.handle_full()
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
