# -*- coding: utf-8 -*-
# @Time : 2023/2/7 10:32
# @Site : https://www.codeminer.cn 
"""
file-name:make_site
ex:
"""
import os

import _init_script
import json
from apps.account.models import SiteData
from utils.md5 import make_uuid

path = os.path.join('../data/site.json')


def save():
    """保存一次"""
    lst = []
    for i in SiteData.objects.all():
        lst.append(
            {
                'name': i.name,
                'img_url': i.img_url,
                'site_url': i.site_url,
                'introduce': i.introduce,
                'datatype': [
                    j.pk for j in i.datatype.all()
                ]
            }
        )
        open(path, 'w', encoding='UTF8').write(json.dumps(lst, ensure_ascii=False))


def run():
    lst = json.loads(open(path, 'r', encoding='UTF8').read())
    l = []
    for item in lst:
        instance = SiteData.objects.create(
            uid=make_uuid().hex,
            name=item['name'],

            site_url=item['site_url'],
            img_url=item['img_url'],
            introduce=item['introduce'])
        instance.datatype.set(item['datatype'])
        instance.save()


if __name__ == '__main__':
    run()
