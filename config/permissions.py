from rest_framework.permissions import BasePermission


class IsAuthenticatedOrOptionsOnly(BasePermission):
    """Доступ если пользователь авторизирован, или
    если метод OPTIONS"""

    def has_permission(self, request, view):
        return bool(
            request.method == "OPTIONS" or
            request.user and
            request.user.is_authenticated
        )
