from rest_framework import serializers

from .models import *


class TakeoutRequestSerializer(serializers.ModelSerializer):
    """Сериализатор для заявки на вынос"""

    class Meta:
        model = TakeoutRequest
        fields = [
            "id",
            "created_at"
        ]
        read_only_fields = [
            "created_at"
        ]
