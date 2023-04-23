# -*- coding: utf-8 -*-
# @Time : 2023/3/29 14:53
# @Site : https://www.codeminer.cn 
"""
file-name:config
ex:
"""
# 消息中间件
from django.conf import settings

broker_url = 'redis://:lzb200244@127.0.0.1:16381/15'
# # 任务执行完存储
result_backend = 'redis://:lzb200244@127.0.0.1:16381/14'

# print(base)
# broker_url = f"""
# amqp://{settings.RABBITMQCONF.get("user")}:{settings.RABBITMQCONF.get("password")}@127.0.0.1:{settings.RABBITMQCONF.get("port")}//
# """
# result_backend = 'rpc://'

# result_backend = f'{base}14'
# broker_url = f'{base}15'
# result_backend = 'rpc://myuser:mypassword@localhost:5672//'
# base = f'{settings.RABBITMQCONF.get("user")}:{settings.RABBITMQCONF.get("password")}@{settings.RABBITMQCONF.get("host", "localhost")}:{settings.RABBITMQCONF.get("port", 5672)}'
# broker_url = f'amqp://{base}//'
# result_backend = f'rpc://{base}//'
#
# task_serializer = 'json'
# result_serializer = 'json'
# accept_content = ['json']
# timezone = 'Asia/Shanghai'
#
# task_routes = {
#     'mycelery.mytasks.*': {'queue': 'default'},
# }
#
# worker_prefetch_multiplier = 1
# worker_max_tasks_per_child = 1
