from rest_framework import serializers

from .models import Container


class FillContainerSerializer(serializers.ModelSerializer):
    """ Сериализатор для заполнения контейнера """
    class Meta:
        model = Container
        fields = ["id", "is_full"]

    def validate_is_full(self, value):
        """ Этот сериализатор используется только для того,
        чтобы заполнить контейнер """
        if not value:
            msg = "is_full can be only true for this view"
            raise serializers.ValidationError(msg)
        return value
