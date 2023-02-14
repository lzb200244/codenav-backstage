# -*- coding: utf-8 -*-
# @Time : 2023/2/14 18:17
# @Site : https://www.codeminer.cn 
"""
file-name:init_data
ex:初始化脚本
"""
import _init_script

from scripts import make_image, make_type, make_categories, make_site


def run():
    for item in [make_image, make_type, make_categories, make_site]:
        item.run()


if __name__ == '__main__':
    run()
    pass
