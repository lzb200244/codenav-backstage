# -*- coding: utf-8 -*-
# @Time : 2023/2/10 15:05
# @Site : https://www.codeminer.cn 
"""
file-name:baseAuth
ex:
"""
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import MethodNotAllowed


class MyBaseAuth(BaseAuthentication):
    response = None

    def authenticate(self, request):
        # meta = request.META
        # if meta.get('HTTP_X_CUSTOM_HEADER') != 'code-miner':
        #     print(meta)
        #     print(meta.get('HTTP_X_CUSTOM_HEADER') )
        #     raise MethodNotAllowed('illegal request')
        pass
