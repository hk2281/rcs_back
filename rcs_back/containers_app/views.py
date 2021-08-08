from rest_framework import generics, permissions, views
from rest_framework.response import Response

from rcs_back.containers_app.models import BuildingPart, Container
from .utils.email import *
from .serializers import *
from .tasks import *


class FillContainerView(generics.UpdateAPIView):
    """ View для заполнения контейнера """
    permission_classes = [permissions.AllowAny]
    serializer_class = FillContainerSerializer
    queryset = Container.objects.filter(status=Container.ACTIVE)

    def perform_update(self, serializer) -> None:
        instance = self.get_object()
        if instance.is_full:
            # Повторное сообщение
            handle_repeat_full_report.delay(instance.pk)
        else:
            # Заполнение контейнера через главную страницу
            handle_first_full_report.delay(instance.pk)
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
                handle_first_full_report.delay(instance.pk)
            if instance.is_full and not serializer.validated_data["is_full"]:
                handle_empty_container.delay(instance.pk)
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


class ContainerPublicAddView(generics.CreateAPIView):
    """Добавление своего контейнера с главной страницы"""
    queryset = Container.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = ContainerPublicAddSerializer

    def perform_create(self, serializer):
        instance = serializer.save(status=Container.WAITING)
        print(instance.pk)
        public_container_add_notify.delay(instance.pk)


class ContainerStatusOptionsView(views.APIView):
    """Статусы для контейнеров"""
    statuses = {
        1: "ожидает подключения",
        2: "активный",
        3: "не активный"
    }

    def get(self, request, *args, **kwargs):
        return Response(self.statuses)


class ContainerKindOptionsView(views.APIView):
    """Виды контейнеров"""
    statuses = {
        1: "экобокс",
        2: "офисная урна",
        3: "коробка из-под бумаги"
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
