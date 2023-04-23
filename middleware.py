import jwt
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from rest_framework.exceptions import AuthenticationFailed

from apps.account.models import UserInfo


class CoreMiddleWare(MiddlewareMixin):
    pass
