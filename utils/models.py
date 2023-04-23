# -*- coding: utf-8 -*-
# @Time : 2023/3/27 14:42
# @Site : https://www.codeminer.cn 
"""
file-name:models
ex:
"""
from django.db import models


class BaseModel(models.Model):
    """基类模型"""
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        abstract = True  # 抽象模型类, 用于继承使用
