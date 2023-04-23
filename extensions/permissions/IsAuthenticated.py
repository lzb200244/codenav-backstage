# -*- coding: utf-8 -*-
# @Time : 2023/4/23 15:33
# @Site : https://www.codeminer.cn 
"""
file-name:IsAuthenticated
ex:
"""
from django.contrib.auth.models import AnonymousUser
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission


class CustomIsAuthenticated(BasePermission):

    def has_permission(self, request, view):
        # 需要登录
        if isinstance(request.user, AnonymousUser):
            raise PermissionDenied({'msg': '请先登录！！', 'code': 1023})
        return True
