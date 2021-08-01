from rest_framework import serializers

from rcs_back.containers_app.models import Container, Building
from rcs_back.takeouts_app.models import *


class ContainersTakeoutRequestSerializer(serializers.ModelSerializer):
    """Для создания заявки на вынос контейнера"""

    containers = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Container.objects.filter(status=Container.ACTIVE)
    )
    emptied_containers = serializers.PrimaryKeyRelatedField(
        many=True, read_only=True
    )

    class Meta:
        model = ContainersTakeoutRequest
        fields = [
            "id",
            "created_at",
            "building",
            "building_part",
            "containers",
            "confirmed_at",
            "emptied_containers",
            "worker_info",
            "mass"
        ]
        read_only_fields = [
            "created_at",
            "confirmed_at",
            "emptied_containers",
            "worker_info"
        ]


class ContainersTakeoutConfirmationSerializer(serializers.ModelSerializer):
    """Для подтверждения выноса контейнеров"""

    containers = serializers.PrimaryKeyRelatedField(
        many=True, read_only=True
    )
    emptied_containers = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Container.objects.filter(status=Container.ACTIVE)
    )

    class Meta:
        model = ContainersTakeoutRequest
        fields = [
            "id",
            "created_at",
            "building",
            "containers",
            "confirmed_at",
            "emptied_containers",
            "worker_info",
            "mass"
        ]
        read_only_fields = [
            "created_at",
            "building",
            "building_part"
            "containers",
            "confirmed_at"
        ]


class TankTakeoutRequestSerializer(serializers.ModelSerializer):
    """Для создания заявки на вывоз бака"""
    building = serializers.PrimaryKeyRelatedField(
        queryset=Building.objects.all()
    )

    class Meta:
        model = TankTakeoutRequest
        fields = [
            "id",
            "created_at",
            "building",
            "confirmed_at",
            "confirmed_mass",
            "wait_time",
            "fill_time",
            "mass"
        ]
        read_only_fields = [
            "created_at",
            "confirmed_at",
            "confirmed_mass"
        ]


class TankTakeoutConfirmationSerializer(serializers.ModelSerializer):
    """Для подтверждения вывоза бака"""
    building = serializers.PrimaryKeyRelatedField(
        read_only=True
    )

    class Meta:
        model = TankTakeoutRequest
        fields = [
            "id",
            "created_at",
            "building",
            "confirmed_at",
            "confirmed_mass",
            "wait_time",
            "fill_time",
            "mass"
        ]
        read_only_fields = [
            "building",
            "created_at",
            "confirmed_at"
        ]


class TakeoutConditionSerializer(serializers.ModelSerializer):
    type = serializers.CharField(source="get_type_display")
    building = serializers.StringRelatedField(
        read_only=True
    )
    building_part = serializers.StringRelatedField(
        read_only=True
    )

    class Meta:
        model = TakeoutCondition
        fields = [
            "id",
            "type",
            "number",
            "building",
            "building_part"
        ]


class AddTakeoutConditionSerializer(serializers.ModelSerializer):
    """Сериализатор с цифрой у типа и для id здания и корпуса"""

    class Meta:
        model = TakeoutCondition
        fields = [
            "id",
            "type",
            "number",
            "building",
            "building_part"
        ]
