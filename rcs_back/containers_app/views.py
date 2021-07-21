from rest_framework import generics, permissions, views
from rest_framework.response import Response
from io import BytesIO
from django.core.files import File

from rcs_back.containers_app.models import BuildingPart, Container
from rcs_back.containers_app.view_utils import *
from .serializers import *
from .qr import generate_sticker


class FillContainerView(generics.UpdateAPIView):
    """ View для заполнения контейнера """
    permission_classes = [permissions.AllowAny]
    serializer_class = FillContainerSerializer
    queryset = Container.objects.filter(status=Container.ACTIVE)

    def perform_update(self, serializer) -> None:
        instance = self.get_object()
        if instance.is_full:
            # Повторное сообщение
            instance.last_full_report().count += 1
            instance.last_full_report().save()
        else:
            """Заполнение контейнера через главную страницу"""
            handle_full_container(instance)
        serializer.save()


class ContainerDetailView(generics.RetrieveUpdateDestroyAPIView):
    """ View для CRUD-операций с контейнерами """
    queryset = Container.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return ContainerSerializer
        else:
            return ChangeContainerSerializer

    def perform_update(self, serializer):
        instance = self.get_object()
        """Изменение заполненности контейнера хоз отделом/эко"""
        if "is_full" in serializer.validated_data:
            if not instance.is_full and serializer.validated_data["is_full"]:
                handle_full_container(instance)
            if instance.is_full and not serializer.validated_data["is_full"]:
                handle_empty_container(instance)
        serializer.save()


class ContainerListView(generics.ListCreateAPIView):
    """ View для CRUD-операций с контейнерами """
    queryset = Container.objects.all()
    filterset_fields = [
        "building",
        "building_part",
        "floor",
        "is_full",
        "status"
    ]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return ContainerSerializer
        else:
            return ChangeContainerSerializer


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


class ContainerPublicAddView(generics.CreateAPIView):
    """Добавление своего контейнера с главной страницы"""
    queryset = Container.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = ContainerPublicAddSerializer

    def perform_create(self, serializer):
        instance = serializer.save(status=Container.WAITING)
        public_container_add_notify(instance)


class ContainerStatusOptionsView(views.APIView):
    """Статусы для контейнеров"""
    statuses = {
        1: "ожидает подключения",
        2: "активный",
        3: "не активный"
    }

    def get(self, request, *args, **kwargs):
        return Response(self.statuses)


class ActivateContainerView(generics.UpdateAPIView):
    """ View для активации контейнера """
    permission_classes = [permissions.AllowAny]
    serializer_class = ActivateContainerSerializer
    queryset = Container.objects.filter(status=Container.WAITING)


class PublicFeedbackView(views.APIView):
    """View для обратной связи на главной странице"""
    serializer_class = PublicFeedbackSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        container_id = 0
        if "container_id" in serializer.validated_data:
            container_id = serializer.validated_data["container_id"]
        msg = serializer.validated_data["msg"]
        send_public_feedback(email, msg, container_id)
        resp = {
            "status": "email sent"
        }
        return Response(resp)


class BuildingPartView(generics.ListAPIView):
    """View списка корпусов"""
    serializer_class = BuildingPartSerializer
    queryset = BuildingPart.objects.all()
    filterset_fields = ["building"]
