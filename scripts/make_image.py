# -*- coding: utf-8 -*-
# @Time : 2023/2/5 8:53
# @Site : https://www.codeminer.cn 
"""
file-name:make_image
ex:
"""
import _init_script

from apps.operation.models import Images

lst = ['ali', 'java', 'python', 'go', 'tencent', 'zhihu', 'csdn', 'cnblogs', 'github', 'git', 'blbl', 'vue',
       '牛客', 'leetcode', 'simplybook']
siteImg = map(lambda x: f'https://defaultdata-1311013567.cos.ap-nanjing.myqcloud.com/{x}.png', lst)

avatar = [f'https://defaultdata-1311013567.cos.ap-nanjing.myqcloud.com/p{i}.png' for i in range(1, 11)]
other = []
opt = [avatar, siteImg, other]


def run():
    for i, v in enumerate(opt, 1):
        # print(Images.objects.all())
        Images.objects.bulk_create(
            [Images(type=i, path=item) for item in v]
        )


if __name__ == '__main__':
    run()
    pass
