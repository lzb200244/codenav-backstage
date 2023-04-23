# -*- coding: utf-8 -*-
# @Time : 2023/3/27 12:28
# @Site : https://www.codeminer.cn 
"""
file-name:response
ex:枚举状态码
"""
from enum import IntEnum


class StatusResponseEnum(IntEnum):
    """操作"""
    # 成功
    Success = 200
    # 提交资源已经创建
    Created = 201
    """
    客户端
    """
    # 参数错误
    BadRequest = 400
    # 认证
    Unauthorized = 401
    # 访问被被禁止
    Forbidden = 403
    # 为找到
    NotFound = 404
    """
    服务的
    """
    # 服务端错误
    ServerError = 405


class CodeResponseEnum(IntEnum):
    """操作"""
    # 成功

    Success = StatusResponseEnum.Success.value + 800
    # 提交资源已经创建
    Created = StatusResponseEnum.Created.value + 800
    """
    客户端
    """
    # 参数错误
    BadRequest = StatusResponseEnum.BadRequest.value + 800
    # 认证
    Unauthorized = StatusResponseEnum.Unauthorized.value + 800
    # 访问被被禁止
    Forbidden = StatusResponseEnum.Forbidden.value + 800
    # 为找到+过期
    NotFound = StatusResponseEnum.NotFound.value + 800
    """
    服务的
    """
    # 服务端错误
    ServerError = StatusResponseEnum.ServerError.value + 800
