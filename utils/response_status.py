# -*- coding: utf-8 -*-
# @Time : 2022/12/24 11:35
# @Site : https://www.codeminer.cn
"""
ex:封装Response
"""

from rest_framework.response import Response


class APIResponse(Response):
    # code=status+800
    def __init__(self, data=None, code=1000, msg='success', status=None, headers=None, **kwargs):
        dic = {'code': code, 'msg': msg}
        if data is not None:
            dic = {'code': code, 'msg': msg, 'data': data}
        dic.update(kwargs)
        super().__init__(data=dic, status=status, headers=headers)


if __name__ == '__main__':
    pass
