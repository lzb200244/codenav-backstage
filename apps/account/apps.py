from django.apps import AppConfig


class App01Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.account'
    verbose_name = '账户'
    verbose_name_plural = '账户'

