from django.contrib import admin

from .models import *


admin.site.register(Container)
admin.site.register(Building)
admin.site.register(FullContainerReport)
admin.site.register(EnoughFullContainersNotification)
