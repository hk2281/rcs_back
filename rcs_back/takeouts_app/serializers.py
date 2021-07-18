from rest_framework import serializers

from rcs_back.containers_app.models import Container, Building
from rcs_back.takeouts_app.models import *


class ContainersTakeoutRequestSerializer(serializers.ModelSerializer):

    containers = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Container.objects.all()
    )

    class Meta:
        model = ContainersTakeoutRequest
        fields = [
            "id",
            "created_at",
            "containers"
        ]
        read_only_fields = [
            "created_at"
        ]


class ContainersTakeoutConfirmationSerializer(serializers.ModelSerializer):

    building = serializers.PrimaryKeyRelatedField(
        many=False, queryset=Building.objects.all()
    )

    containers = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Container.objects.filter(is_active=True)
    )

    class Meta:
        model = ContainersTakeoutConfirmation
        fields = [
            "id",
            "building",
            "containers",
            "worker_info"
        ]


class TankTakeoutRequestSerializer(serializers.ModelSerializer):
    building = serializers.PrimaryKeyRelatedField(
        queryset=Building.objects.all()
    )

    class Meta:
        model = TankTakeoutRequest
        fields = [
            "id",
            "created_at",
            "building"
        ]
        read_only_fields = [
            "created_at"
        ]
