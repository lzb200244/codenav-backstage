# -*- coding: utf-8 -*-
# @Time : 2022/12/24 10:05
# @Site : https://www.codeminer.cn
import jwt
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed, ParseError
from apps.account.models import UserInfo
from django.conf import settings

"""
ex:自定义jwt认证类
"""


class JWTAuthentication(BaseAuthentication):
    """jwt认证类"""

    def authenticate(self, request):
        # 获取jwt_token
        jwt_token = request.META.get("HTTP_TOKEN")

        # 可以来说是为登录的用户
        if jwt_token is None:
            print(jwt_token)
            raise AuthenticationFailed(detail={'code': 1201, 'msg': '需要登录！！'})
        # 存在登录过的用户
        salt = settings.JWT_CONF.get('salt', settings.SECRET_KEY)  # 盐
        typ = settings.JWT_CONF.get('typ', 'HS256')  #

        try:
            payload = jwt.decode(
                jwt_token, salt, typ
            )

        except jwt.exceptions.ExpiredSignatureError:
            # 1101 过期
            raise AuthenticationFailed(detail={'code': 1201, 'msg': 'token认证失效', 'data': ''})
        except jwt.exceptions.DecodeError:
            # 解码错误
            raise AuthenticationFailed(detail={'code': 1201, 'msg': 'token错误', 'data': ''}, )
        except jwt.exceptions.InvalidTokenError:
            # 非法token
            raise AuthenticationFailed(detail={'code': 1201, 'msg': '非法token', 'data': ''})
        user_obj = UserInfo.objects.filter(username=payload.get('name'))
        if not user_obj.exists():
            raise AuthenticationFailed(detail={'code': 1201, 'msg': '需要登录！！'})
        return user_obj.first(), jwt_token  # 认证通过


class JWTAuthentication2(BaseAuthentication):
    """jwt认证类"""

    def authenticate(self, request):
        # 获取jwt_token
        jwt_token = request.COOKIES.get('code-token')

        # 可以来说是为登录的用户
        if jwt_token is None:
            return None
        # 存在登录过的用户
        salt = settings.JWT_CONF.get('salt', settings.SECRET_KEY)  # 盐
        typ = settings.JWT_CONF.get('typ', 'HS256')  #
        try:
            payload = jwt.decode(
                jwt_token, salt, typ
            )

        except jwt.exceptions.ExpiredSignatureError:
            # 1101 过期
            raise AuthenticationFailed(detail={'code': 1201, 'msg': 'token认证失效', 'data': ''})
        except jwt.exceptions.DecodeError:
            # 解码错误
            raise AuthenticationFailed(detail={'code': 1201, 'msg': 'token错误', 'data': ''}, )
        except jwt.exceptions.InvalidTokenError:
            # 非法token
            raise AuthenticationFailed(detail={'code': 1201, 'msg': '非法token', 'data': ''})
        try:
            user = UserInfo.objects.get(username=payload.get('name'))
        except UserInfo.DoesNotExist:
            raise AuthenticationFailed(detail={'code': 1201, 'msg': '非法token', 'data': ''})
        return user, jwt_token  # 认证通过
