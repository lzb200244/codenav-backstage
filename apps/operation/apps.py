from django.apps import AppConfig


class OperationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.operation'
    verbose_name = '用户操作'
    verbose_name_plural = '用户操作'
