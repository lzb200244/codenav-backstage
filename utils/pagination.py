"""分页器"""
import base64

from rest_framework.pagination import PageNumberPagination, CursorPagination


# LimitOffsetPagination, CursorPagination,
class MyPagination(PageNumberPagination):
    page_size = 9
    page_query_param = "page"
    page_size_query_param = "size"

    def get_page_number(self, request, paginator):

        page_number = request.query_params.get(self.page_query_param, 1)
        # if page_number != 1:
        #     page_number = base64.b64decode(str(page_number).encode('utf8')).decode()

        if page_number in self.last_page_strings:
            page_number = paginator.num_pages
        return page_number
#     def get_next_link(self):
#         return True
# super(MyPagination, self).get_next_link()

# class MyPagination(LimitOffsetPagination):
#     default_limit = 9
#     limit_query_param = "page"
#     offset_query_param = "offset"

# class MyPagination(CursorPagination):
#     """游标加密分页"""
#     cursor_query_param = "cursor"  # 游标请求参数，相当于page页数，但该数据是加密的，来自于上次分页返回
#     page_size = 3  # 默认每页显示的
#     ordering = "-pk"  # 排序 根据id倒序
#
#     def get_paginated_response(self, data):
#         print(data)
#
#         return super(MyPagination, self).get_paginated_response(data)
# def get_next_link(self):
#     print(self.has_next)
#     print(self.has_previous)
#
#     return  super(MyPagination, self).get_next_link()

# cursor_query_param = 'page'
# page_size = 9
# ordering = 'pk'  # 排序字段
