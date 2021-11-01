from rest_framework.mixins import UpdateModelMixin
from rest_framework.response import Response


class UpdateThenRetrieveModelMixin(UpdateModelMixin):
    """Mixin, чтобы PUT/PATCH запросы для изменения
    данных использовали один сериализатор,
    а в ответе другой"""
    retrieve_serializer = None  # Нужно задать
    update_serializer = None

    def update(self, request, *args, **kwargs):
        """Оригинальный код"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        """Изменённая строчка"""
        return Response(self.retrieve_serializer(instance).data)
