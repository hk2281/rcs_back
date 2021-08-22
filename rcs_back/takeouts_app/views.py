from django.utils import timezone
from rest_framework import generics, views, permissions
from rest_framework.response import Response

from rcs_back.utils.mixins import UpdateThenRetrieveModelMixin
from rcs_back.takeouts_app.models import *
from rcs_back.takeouts_app.serializers import *
from rcs_back.takeouts_app.utils import *
from rcs_back.containers_app.models import Building
from rcs_back.containers_app.tasks import handle_empty_container


class ContainersTakeoutListView(generics.ListCreateAPIView):
    """CR для заявки на вынос контейнеров"""
    serializer_class = ContainersTakeoutRequestSerializer
    queryset = ContainersTakeoutRequest.objects.all()

    def perform_create(self, serializer):
        instance = serializer.save()
        containers_takeout_notify(request=instance)


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
            handle_empty_container.delay(container.pk)


class TankTakeoutRequestListView(generics.ListCreateAPIView):
    serializer_class = TankTakeoutRequestSerializer
    queryset = TankTakeoutRequest.objects.all()

    def perform_create(self, serializer):
        instance = serializer.save()
        tank_takeout_notify(instance.building)


class TankTakeoutConfirmationView(generics.UpdateAPIView):
    """View для создания подтверждения вывоза бака"""
    serializer_class = TankTakeoutConfirmationSerializer
    queryset = TankTakeoutRequest.objects.filter(
        confirmed_at__isnull=True
    )

    def perform_update(self, serializer):
        serializer.save(confirmed_at=timezone.now())


class TakeoutConditionListView(generics.ListCreateAPIView):
    queryset = TakeoutCondition.objects.all()
    filterset_fields = ["building", "building_part"]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return AddTakeoutConditionSerializer
        else:
            return TakeoutConditionSerializer


class TakeoutConditionDetailView(UpdateThenRetrieveModelMixin,
                                 generics.RetrieveUpdateDestroyAPIView):
    queryset = TakeoutCondition.objects.all()
    retrieve_serializer = TakeoutConditionSerializer
    update_serializer = AddTakeoutConditionSerializer

    def get_serializer_class(self):
        if self.request.method == "GET":
            return self.retrieve_serializer
        else:
            return self.update_serializer


class CollectedMassView(views.APIView):
    """Статистика собранной массы макулатуры для главной страницы"""
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        resp = {}
        for building in Building.objects.all():
            building_dict = {}
            building_dict["total"] = building.collected_mass()
            for building_part in building.building_parts.all():
                building_dict[str(building_part)
                              ] = building_part.collected_mass()
            resp[str(building)] = building_dict
        return Response(resp)
