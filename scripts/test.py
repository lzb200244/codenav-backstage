import _init_script
from django_redis import get_redis_connection
import redis
import datetime
import json

from utils.cal_week import set_score, get_week_key
import requests


print(get_week_key())

conn = get_redis_connection('account')
print(conn.keys())
dic = {
    'username': 'lzb威威',
    'avatar': 'https//casasd2/'
}

# conn.zincrby('WEEK_RANK:2023-02-06', 12, json.dumps(dic,ensure_ascii=False))
# conn.zincrby('WEEK_RANK:2023-02-06', 12, json.dumps(dic,ensure_ascii=True))
# 第一到最后
# set_score(conn, 'WEEK_RANK:2023-02-06', 1, '200244')
# print(conn.zrank('WEEK_RANK:2023-02-06', '2632141215'))
print(conn.zrange('WEEK_RANK:2023-02-13', 0, -1, withscores=True))
#
# # ZREVRANK
# print(conn.zrevrank('WEEK_RANK:2023-02-06', '2632141215')+1)
# set_score(conn, 'WEEK_RANK:2023-02-06',5, '2632141215')
# for i in conn.zrange('WEEK_RANK:2023-02-06', 0, -1, withscores=True):
#     conn.zrem('WEEK_RANK:2023-02-06',i[0])
