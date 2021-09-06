from rest_framework import serializers

from .models import BuildingPart, Container, Building, FullContainerReport


class BuildingPartSerializer(serializers.ModelSerializer):
    class Meta:
        model = BuildingPart
        fields = [
            "id",
            "num"
        ]


class BuildingSerializer(serializers.ModelSerializer):
    """Сериализатор здания"""
    building_parts = BuildingPartSerializer(
        many=True, read_only=True
    )

    class Meta:
        model = Building
        fields = [
            "id",
            "address",
            "itmo_worker_email",
            "building_parts"
        ]


class BuildingShortSerializer(serializers.ModelSerializer):
    """Сериализатор здания только с адресом"""
    class Meta:
        model = Building
        fields = [
            "id",
            "address"
        ]


class FullContainerReportSerializer(serializers.ModelSerializer):
    """Сериализатор для заполнения контейнера"""
    container = serializers.PrimaryKeyRelatedField(
        queryset=Container.objects.filter(status=Container.ACTIVE)
    )

    class Meta:
        model = FullContainerReport
        fields = [
            "id",
            "container"
        ]


class ContainerSerializer(serializers.ModelSerializer):
    """ Сериализатор контейнера"""
    building = BuildingShortSerializer()
    building_part = BuildingPartSerializer()

    class Meta:
        model = Container
        fields = [
            "id",
            "kind",
            "mass",
            "building",
            "building_part",
            "floor",
            "room",
            "description",
            "is_full",
            "status",
            "requested_activation",
            "email",
            "phone",
            "cur_fill_time",
            "cur_takeout_wait_time",
            "avg_fill_time",
            "avg_takeout_wait_time"
        ]


class ChangeContainerSerializer(serializers.ModelSerializer):
    """ Сериализатор контейнера с id у здания и корпуса"""

    class Meta:
        model = Container
        fields = [
            "id",
            "building",
            "building_part",
            "kind",
            "floor",
            "room",
            "description",
            "status",
            "email",
            "phone",
        ]


class ContainerPublicAddSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления контейнера рандомами"""

    class Meta:
        model = Container
        fields = [
            "id",
            "email",
            "phone",
            "building",
            "building_part",
            "floor",
            "room",
            "description",
            "kind"
        ]
        extra_kwargs = {
            "email": {"required": True},
            "phone": {"required": True}
        }


class PublicFeedbackSerializer(serializers.Serializer):
    """Сериализатор для оставления обратной связи"""
    email = serializers.EmailField()
    container_id = serializers.IntegerField(required=False)
    msg = serializers.CharField(max_length=4096)
