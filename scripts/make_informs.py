# -*- coding: utf-8 -*-
# @Time : 2023/2/7 15:58
# @Site : https://www.codeminer.cn 
"""
file-name:make_informs
ex:
"""
import _init_script
import random
from apps.operation.models import Inform


def run():
    Inform.objects.bulk_create([Inform(
        type=random.randint(1, 5),
        content=i*'撒打算',
        user_id=1
    ) for i in range(30)])


"""创建测试消息"""
if __name__ == '__main__':
    run()
