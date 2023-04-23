import os

import _init_script
from apps.account.models import SiteData
from mycelery.mytasks.email.tasks import send_user_email

# site_data_list = SiteData.objects.select_related('recommend')
# for site_data in site_data_list:
#     # 在循环内使用相关属性，例如
#     print(site_data.recommend.username)
    # for user in site_data.sitedatauser:
    #     print(user)
site_data_list = SiteData.objects.prefetch_related('datatype')
print(site_data_list  )
for site_data in site_data_list:
    # 在循环内使用相关属性，例如
    for category in site_data.datatype:
        print(category.name)
# from typing import Union, Tuple, List
#
# x: Union[str, int] = 1
# y: List[bool] = [False]
#

# # from typing import NewType, MappingView
# #
# # UserId = NewType('UserId', MappingView[int, str])
# #
# #
# # def get_user_name(user_id: UserId) -> str:
# #     ...
#
#
# from enum import Enum
#
#
# class StatusEnum(Enum):
#     SUCCESS = 200
#     pass
#
#
# print(StatusEnum.SUCCESS.value)
#
# # typechecks
#
# # user_a = get_user_name(UserId(42351))
#
# # does not typecheck; an int is not a UserId
#
# # user_b = get_user_name(UserId(123))
# import inspect
# import importlib
#
# # Replace 'filename' with the path of the file you want to extract classes from
# filename = 'cc.py'
#
# # Get the module object for the file
# module = importlib.import_module(filename)
#
# # Get all members of the module and filter for classes
# classes = [m[1] for m in inspect.getmembers(module, inspect.isclass)]
#
# # Print the names of all classes found
# for c in classes:
#     print(c.__name__)
