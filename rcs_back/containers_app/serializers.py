from rest_framework import serializers

from .models import Building, BuildingPart, Container, FullContainerReport
from rcs_back.users_app.models import User

class BuildingPartSerializer(serializers.ModelSerializer):
    class Meta:
        model = BuildingPart
        fields = [
            "id",
            "num"
        ]

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'phone', 'building']

class BuildingAddSerializer(serializers.ModelSerializer):
    "Сериализатор добавления здания"

    passage_scheme = serializers.ImageField(required=False)  # Поле для загрузки изображения

    class Meta:
        model = Building
        fields = [
            'id','address', 'get_container_room', 'get_sticker_room', 'sticker_giver',
            '_takeout_notified', 'precollected_mass', 'passage_scheme', 'detect_building_part'
        ]



class BuildingPartAddSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления корпуса здания"""

    class Meta:
        model = BuildingPart
        fields = [
            'id','num', 'building'
        ]



class AsignBuildingToUserSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления здания юзеру"""

    building = serializers.PrimaryKeyRelatedField(
        queryset=Building.objects.all(),
        many=True
    )

    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'phone', 'building']


class PasswordSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)

class AsignUsersToBuildingsSerializer(serializers.Serializer):
    user_ids = serializers.ListField(
        child=serializers.IntegerField(),  # Список целых чисел
        required=False,  # Этот параметр не обязателен
        allow_empty=True  # Разрешает пустой список
    )

class BuildingSerializer(serializers.ModelSerializer):
    """Сериализатор здания"""
    building_parts = BuildingPartSerializer(
        many=True, read_only=True
    )
    passage_scheme = serializers.SerializerMethodField()
    class Meta:
        model = Building
        fields = [
            "id",
            "address",
            "building_parts",
            "detect_building_part",
            "sticker_giver",
            "get_container_room",
            "get_sticker_room",
            "_takeout_notified",
            "precollected_mass",
            "detect_building_part",
            "passage_scheme"
        ]
    def get_passage_scheme(self, obj):
        # Возвращаем только имя файла без пути
        return obj.passage_scheme.name if obj.passage_scheme else None


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


class PublicFeedbackSerializer(serializers.Serializer):  # pylint: disable=abstract-method
    """Сериализатор для оставления обратной связи"""
    email = serializers.EmailField()
    container_id = serializers.IntegerField(required=False)
    msg = serializers.CharField(max_length=4096)
