from rest_framework import serializers

from rcs_back.containers_app.models import Container, Building
from rcs_back.takeouts_app.models import *


class ContainersTakeoutRequestSerializer(serializers.ModelSerializer):
    """Для создания заявки на вынос контейнера"""

    building = serializers.PrimaryKeyRelatedField(
        queryset=Building.objects.all()
    )
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

    building = serializers.PrimaryKeyRelatedField(
        read_only=True
    )
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
