from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from .templateManager import service_provider as sp
from rcs_back.containers_app.serializers import UserSerializer

User = get_user_model()

class IsSuperUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_superuser

class RetrieveCurrentUserView(APIView):
    """Возвращает информацию о текущем пользователе"""

    def get(self, request, *args, **kwargs):

        has_eco_group = False
        if request.user.groups.filter(name=settings.ECO_GROUP):
            has_eco_group = True

        resp = {}
        resp["id"] = request.user.pk
        resp["email"] = request.user.email
        resp["has_eco_group"] = has_eco_group
        resp["is_super_user"] = request.user.is_superuser
        if request.user.building:
            resp["building"] = list(request.user.building.values_list("pk", flat=True))
        else:
            resp["building"] = None
        return Response(resp)
    
    def patch(self, request, *args, **kwargs):
        print('hi')
        return Response(status=400)

class UserListView(generics.ListAPIView):
    """View для получения списка пользователей"""
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [IsSuperUser]


class TemplateManager(APIView):
    """занимается обработкой mail шаблонов"""
    
    def get(self, request, *arg, **kwargs):
        mail_manager = sp.MailTemplateServise
        resp =mail_manager.get_all_templates()
        return Response(resp)
    
    def post(self, request, *args, **kwargs):
        print(request)
        reseive_template: dict = request.data
        mail_manager = sp.MailTemplateServise
        try:
            template_name = reseive_template.get('media')
            mail_manager.current_template =  template_name
        except KeyError:
            return Response(status=403, data=f'шаблона с переданным именем: {template_name} не существкет')
        mail_manager.save(reseive_template)
        return Response('hi')
    
