from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.db.models import Q
from rest_framework import generics, permissions, views, status
from rest_framework.response import Response
from tempfile import NamedTemporaryFile

from rcs_back.utils.mixins import UpdateThenRetrieveModelMixin
from rcs_back.containers_app.models import *
from .utils.email import *
from .utils.qr import generate_sticker
from .serializers import *
from .tasks import *


class FullContainerReportView(generics.CreateAPIView):
    """View для заполнения контейнера"""
    permission_classes = [permissions.AllowAny]
    serializer_class = FullContainerReportSerializer

    def perform_create(self, serializer) -> None:
        if "container" in serializer.validated_data:
            container = serializer.validated_data["container"]
            by_staff = self.request.user.is_authenticated
            if container.last_full_report():
                # Повторное сообщение о заполнении
                handle_repeat_full_report.delay(
                    container.pk,
                    by_staff
                )
            else:
                # Первое сообщение
                handle_first_full_report.delay(
                    container.pk,
                    by_staff
                )


class ContainerDetailView(UpdateThenRetrieveModelMixin,
                          generics.RetrieveUpdateDestroyAPIView):
    """ View для CRUD-операций с контейнерами """
    queryset = Container.objects.filter(
        ~Q(status=Container.RESERVED)
    )
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    retrieve_serializer = ContainerSerializer
    update_serializer = ChangeContainerSerializer

    def get_serializer_class(self):
        if self.request.method == "GET":
            return self.retrieve_serializer
        else:
            return self.update_serializer


class ContainerListView(generics.ListAPIView):
    """ View для CRUD-операций с контейнерами """

    serializer_class = ContainerSerializer

    filterset_fields = [
        "building",
        "building_part",
        "floor",
        "status"
    ]

    allowed_sorts = [
        "building",
        "building_part",
        "floor",
        "status"
    ]

    def get_queryset(self):
        """Сортировка"""
        queryset = Container.objects.filter(
            ~Q(status=Container.RESERVED)
        )
        if (self.request.user.is_authenticated and
            self.request.user.groups.filter(
                name=settings.HOZ_GROUP) and
                self.request.user.building):
            queryset = queryset.filter(
                building=self.request.user.building
            )
        if "is_full" in self.request.query_params:
            is_full_param = self.request.query_params.get("is_full")
            is_full = False if is_full_param == "false" else True
            queryset = Container.objects.filter(
                _is_full=is_full
            )

        if "sort_by" in self.request.query_params:
            sort = self.request.query_params.get("sort_by")

            if sort not in self.allowed_sorts:
                return queryset

            if sort == "is_full":
                sort = "_is_full"  # Чтобы не путать фронт

            if "order_by" in self.request.query_params:
                order_by = self.request.query_params.get("order_by")
                if order_by == "desc":
                    sort = "-" + sort

            return queryset.order_by(sort)

        return queryset


class BuildingListView(generics.ListAPIView):
    """Списко зданий (для опций при создании контейнера)"""
    serializer_class = BuildingSerializer
    queryset = Building.objects.all()
    permission_classes = [permissions.AllowAny]


class ContainerPublicAddView(generics.CreateAPIView):
    """Добавление своего контейнера с главной страницы"""
    queryset = Container.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = ContainerPublicAddSerializer

    def perform_create(self, serializer):
        building = serializer.validated_data["building"]

        """Если в заданном здании есть распечатанные стикеры,
        то нужно использовать их id"""
        if Container.objects.filter(
            status=Container.RESERVED
        ).filter(
            building=building
        ).exists():
            container: Container = Container.objects.filter(
                status=Container.RESERVED
            ).filter(
                building=building
            ).first()
            container.email = serializer.validated_data["email"]
            container.phone = serializer.validated_data["phone"]
            if "building_part" in serializer.validated_data:
                container.building_part = serializer.validated_data[
                    "building_part"]
            else:
                container.building_part = container.detect_building_part()
            container.floor = serializer.validated_data["floor"]
            if "room" in serializer.validated_data:
                container.room = serializer.validated_data["room"]
            if "description" in serializer.validated_data:
                container.description = serializer.validated_data[
                    "description"]
            container.kind = serializer.validated_data["kind"]
            container.status = Container.WAITING
            container.save()

        else:
            container = serializer.save(status=Container.WAITING)
            container.building_part = container.detect_building_part()
            container.save()

        public_container_add_notify.delay(container.pk)


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


class EmptyContainerView(views.APIView):
    """View для отметки контейнера пустым
    экоотделом"""

    def post(self, request, *args, **kwargs):
        if "pk" in self.kwargs:
            container = Container.objects.filter(
                pk=self.kwargs["pk"]
            ).first()
            if container:
                last_report = container.last_full_report()
                if last_report:
                    """Этот view используется для корректировки
                    ошибок, поэтому не вызываем handle_empty_container
                    (там устанавливается время опустошения)"""
                    last_report.delete()
                    container._is_full = False  # Для сортировки
                    container.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


class ContainerStickerView(views.APIView):
    """Возвращает стикер контейнера"""
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        with NamedTemporaryFile() as tmp:
            fname = f"container-sticker-{self.kwargs['pk']}"
            sticker_im = generate_sticker(self.kwargs["pk"])
            sticker_im.save(tmp.name, "pdf", quality=100)
            file_data = tmp.read()
            response = HttpResponse(
                file_data,
                headers={
                    "Content-Type": "application/pdf",
                    "Content-Disposition":
                    f'attachment; filename={fname}'
                }
            )
            return response


class ContainerActivationRequestView(views.APIView):
    """View для запроса активации контейнером"""
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        container = get_object_or_404(
            Container, pk=self.kwargs["pk"]
        )
        if container.status != container.WAITING:
            resp = {
                "error": "This container has already been activated"
            }
            return Response(
                resp,
                status=status.HTTP_400_BAD_REQUEST
            )
        if container.requested_activation:
            resp = {
                "error": "This container has already requested activation"
            }
            return Response(
                resp,
                status=status.HTTP_400_BAD_REQUEST
            )

        container.request_activation()

        resp = {
            "success": "email sent"
        }
        return Response(resp)


class ContainerActivationView(views.APIView):
    """View для активации контейнера через письмо"""
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        container = get_object_or_404(
            Container, pk=self.kwargs["pk"]
        )
        if container.is_active():
            title = "Повторная активация"
            text = "Контейнер уже был активирован"
            status = "info"
        elif "token" in self.request.query_params:
            r_token = self.request.query_params.get("token")
            token: EmailToken = EmailToken.objects.filter(
                token=r_token
            ).first()
            if token and not token.is_used:
                container.activate()
                token.use()
                title = "Успешная активация"
                text = "Контейнер успешно активирован"
                status = "success"
            elif token:
                title = "Повторная активация"
                text = "Контейнер уже был активирован"
                status = "info"
            else:
                title = "Ошибка активации"
                text = "Неверный токен для активации"
                status = "error"
        else:
            title = "Ошибка активации"
            text = "Неверный токен для активации"
            status = "error"
        redirect_path = f"/result?title={title}&text={text}&status={status}"
        return HttpResponseRedirect(
            redirect_to="https://" + settings.DOMAIN + redirect_path
        )


class ContainerCountView(views.APIView):
    """Количество контейнеров по зданиям"""
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        resp = []
        building: Building
        for building in Building.objects.all():
            building_dict = {}
            building_dict["id"] = building.pk
            building_dict["building"] = building.street_name()
            building_dict["count"] = building.container_count()
            # В тоннах до десятых
            building_dict["mass"] = building.confirmed_collected_mass(
            ) // 100 / 10
            resp.append(building_dict)
        return Response(resp)
