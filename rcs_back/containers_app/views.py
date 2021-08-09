from rest_framework import generics, permissions, views
from rest_framework.response import Response

from rcs_back.containers_app.models import BuildingPart, Container
from .utils.email import *
from .serializers import *
from .tasks import *


class FullContainerReportView(generics.CreateAPIView):
    """View для заполнения контейнера"""
    permission_classes = [permissions.AllowAny]
    serializer_class = FullContainerReportSerializer

    def perform_create(self, serializer) -> None:
        if "container" in serializer.validated_data:
            container = serializer.validated_data["container"]
            if container.is_full():
                # Повторное сообщение
                handle_repeat_full_report.delay(container.pk)
            else:
                # Заполнение контейнера через главную страницу
                handle_first_full_report.delay(container.pk)


class ContainerDetailView(generics.RetrieveUpdateDestroyAPIView):
    """ View для CRUD-операций с контейнерами """
    queryset = Container.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return ContainerSerializer
        else:
            return ChangeContainerSerializer


class ContainerListView(generics.ListCreateAPIView):
    """ View для CRUD-операций с контейнерами """
    queryset = Container.objects.all()
    filterset_fields = [
        "building",
        "building_part",
        "floor",
        "status"
    ]

    def get_queryset(self):
        if "is_full" in self.request.query_params:
            #  Если такая фильтрация станет слишком медленной,
            #  то надо будет добавить поле для модели и фильтровать
            #  по нему
            is_full = self.request.query_params.get("is_full")
            val = True if is_full == "true" else False
            ids = []
            for container in Container.objects.all():
                if container.is_full() == val:
                    ids.append(container.id)
            return Container.objects.filter(id__in=ids)
        else:
            return Container.objects.all()

    def get_serializer_class(self):
        if self.request.method == "GET":
            return ContainerSerializer
        else:
            return ChangeContainerSerializer


class BuildingListView(generics.ListAPIView):
    """Списко зданий (для опций при создании контейнера)"""
    serializer_class = BuildingSerializer
    queryset = Building.objects.all()
    permission_classes = [permissions.AllowAny]


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
    permission_classes = [permissions.AllowAny]
