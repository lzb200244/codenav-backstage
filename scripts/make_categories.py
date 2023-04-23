import json

import _init_script
from apps.account.models import Categories
import os

path = os.path.join('../data/categories.json')


def save():
    open(path, 'w', encoding='UTF8').write(

        json.dumps(list(Categories.objects.values('categories', 'type')), ensure_ascii=False
                   )
    )


def run():
    lst = json.loads(open(path, 'r', encoding='UTF8').read())
    Categories.objects.bulk_create(
        [Categories(type_id=item['type'], categories=item['categories']) for item in lst])


if __name__ == '__main__':
    # save()
    # run()
    pass
