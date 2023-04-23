# -*- coding: utf-8 -*-
# @Time : 2023/3/23 9:11
# @Site : https://www.codeminer.cn 
"""
file-name:redis_mixin
ex:
"""
import abc


class CatchWithRedisMixin(metaclass=abc.ABCMeta):
    """用于缓存读取"""
    conn_slot = 'catch'
    conn = None

    def __init__(self, ):
        self.conn = self.get_con()

    @abc.abstractmethod
    def get_con(self): pass
