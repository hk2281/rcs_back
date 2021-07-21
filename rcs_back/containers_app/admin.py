from django.contrib import admin

from .models import *


class ContainerAdmin(admin.ModelAdmin):
    readonly_fields = [
        "cur_fill_time",
        "cur_takeout_wait_time",
        "avg_fill_time",
        "avg_takeout_wait_time"
    ]


admin.site.register(Container, ContainerAdmin)
admin.site.register(Building)
admin.site.register(BuildingPart)
admin.site.register(FullContainerReport)
admin.site.register(TakeoutConditionMet)
