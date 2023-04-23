from django.contrib import admin
from apps.hall import models


@admin.register(models.ChatModel)
class ChatAdmin(admin.ModelAdmin):
    pass


@admin.register(models.StimulateModel)
class StimulateAdmin(admin.ModelAdmin):
    pass


@admin.register(models.CustomRecord)
class CustomRecordAdmin(admin.ModelAdmin):
    pass
