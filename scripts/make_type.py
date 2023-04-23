# -*- coding: utf-8 -*-
# @Time : 2023/2/4 21:44
# @Site : https://www.codeminer.cn 
"""
file-name:make_type
ex:
"""
import _init_script
from apps.account.models import Type


def run():
    s = [Type(type=i, pk=i) for i, v in Type.TYPE_CHOICES]
    Type.objects.bulk_create(s)


if __name__ == '__main__':
    run()
