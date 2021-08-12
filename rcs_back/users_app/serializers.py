from django.contrib.auth import authenticate
from rest_framework import serializers, exceptions
from rest_framework_simplejwt.serializers import (
    TokenObtainSerializer as OriginalTokenObtainSerializer,
    TokenObtainPairSerializer as OriginalTokenObtainPairSerializer
)

from rcs_back.users_app.models import User


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для подтверждения пользователя"""
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "is_confirmed"
        ]
        read_only_fields = [
            "email"
        ]


class TokenObtainSerializer(OriginalTokenObtainSerializer):
    """Изменённый сериализатор для проверки подтверждения
    пользователя и разных error messages"""

    default_error_messages = {
        "unconfirmed": "Этот аккаунт не был подтверждён сотрудником",
        "inactive": ("Почта, указанная при регистрации аккаунта, "
                     "не была подтверждена"),
        "not_found": "Не найден пользователь с такими почтой и паролем"
    }

    def validate(self, attrs):
        authenticate_kwargs = {
            self.username_field: attrs[self.username_field],
            'password': attrs['password'],
        }
        try:
            authenticate_kwargs['request'] = self.context['request']
        except KeyError:
            pass

        self.user = authenticate(**authenticate_kwargs)

        #  Изменённый код
        if not self.user:
            raise exceptions.AuthenticationFailed(
                self.error_messages["not_found"],
                "not_found",
            )
        if not self.user.is_active:
            raise exceptions.AuthenticationFailed(
                self.error_messages["inactive"],
                "inactive",
            )
        if not self.user.is_confirmed:
            raise exceptions.AuthenticationFailed(
                self.error_messages["unconfirmed"],
                "unconfirmed",
            )

        return {}


class TokenObtainPairSerializer(OriginalTokenObtainPairSerializer,
                                TokenObtainSerializer):
    """Наследуется от класса выше"""
    pass
