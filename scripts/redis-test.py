# -*- coding: utf-8 -*-
# @Time : 2023/3/24 14:37
# @Site : https://www.codeminer.cn 
"""
file-name:redis-text
ex:
"""
import _init_script
from django_redis import get_redis_connection
import redis

conn = get_redis_connection('hall')

# raise EOFError
# conn.sadd('1', '2')
# conn.sadd('1', '3')
conns = redis.Redis()

# 返回用户所有的关注对象
# print(conn.smembers('1'))
# conn.sadd('2', 1)
# conn.sadd('2', 3)
# conn.sadd('2', 6)

print(1, conn.smembers('1'))
print(2, conn.smembers('2'))
print(3, conn.smembers('3'))
print(4, conn.smembers('4'))
print(5, conn.smembers('5'))
print(6, conn.smembers('6'))
# 获取交集
# print(conn.sinter([1, 2]))

# 好友共同关注
"""
1的好友2,3,5
2 的好友 134
3 的好友 1246
4 没有好友
5 好友 6
6 没有
此时1的好友2,3都关注了4这个用户,那么就给1推荐这个用户
好友3和5关注了6=>6
"""
# 先找到1的好友
# todo 组合问题
print("--" * 50)
print("1的好友:", conn.smembers("1"))
# (2,3)(2,5)(3,5)
lst = conn.smembers("1")

import itertools

comb = itertools.combinations(lst, 2)
sets = set([])
# print(list(comb))
for item in comb:
    print("-" * 50)
    print(item)
    sets.update(conn.sinter(item))
    print('推荐:', conn.sinter(item))
print(sets)
# def combination(l, idx):
#     for i, item in enumerate(l[idx:]):
#         print(l[i:])
#     pass
#
#
# combination(list(lst), 0)
print("-" * 50)
dic = {b'4', b'6', b'2'}  # 共同关注
dic2 = {b'3', b'5', b'2'}  # 已经关注

print(dic)
# 差集
print(dic.difference(dic2))
