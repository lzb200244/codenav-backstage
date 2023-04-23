from django.contrib import admin
from django.utils.safestring import mark_safe
from apps.operation import models


@admin.register(models.Comments)  # 第一个参数可以是列表
class CommentsAdmin(admin.ModelAdmin):
    list_display = ['creator', "content", "reply_site", "parentId", 'like', "create_time", ]
    ordering = ["-create_time"]  # 按id降序排序
    list_per_page = 10  # 列表每页显示条数
    list_filter = ['create_time', 'reply_site']


@admin.register(models.Images)
class ImageAdmin(admin.ModelAdmin):

    def show_path(self, obj):
        return mark_safe(
            f"<img  src='{obj.path}' width='30'  style=' border-radius: 50%;'/>"
        )

    list_display = ['path', 'type']
    show_path.short_description = "图库"


@admin.register(models.Inform)
class Informdmin(admin.ModelAdmin):
    pass


@admin.register(models.News)
class NewsAdmin(admin.ModelAdmin):
    pass


@admin.register(models.BillBoard)
class BillBoardAdmin(admin.ModelAdmin):
    pass
