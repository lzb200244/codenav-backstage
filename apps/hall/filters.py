from django_filters import rest_framework as filters

from apps.hall.models import ChatModel, CustomRecord, StimulateModel


class ChatFilter(filters.FilterSet):
    # 过滤大小写标题
    title = filters.CharFilter(field_name='title', lookup_expr='icontains')
    type = filters.CharFilter(field_name='issue_type', lookup_expr='icontains')
    order = filters.CharFilter(method="order_filter")

    # chatId, issue_type, opt, title
    class Meta:
        model = ChatModel  # 模型名
        fields = ['title', 'issue_type']
        exclude = ['content', 'creator', 'replay', 'create_time']

    def order_filter(self, queryset, name, value):
        if value == 'recommend':
            return queryset.order_by('create_time')
        elif value == 'latest':

            return queryset.order_by('-create_time')
        elif value == 'hot':
            return queryset.order_by('-like')
        return queryset


class CircleFilter(filters.FilterSet):
    type = filters.CharFilter(method="type_filter")

    def __init__(self, conn, *args, **kwargs):
        self.conn = conn
        super(CircleFilter, self).__init__(*args, **kwargs)

    class Meta:
        model = ChatModel  # 模型名
        fields = ['type']

    def type_filter(self, queryset, name, value):
        if value == 'common':
            """共同关注"""
            # 用户关注的人
            pk = self.request.user.pk
            user_attention = self.conn.smembers(pk)
            # 只要有大于2的就是说明共同关注(todo 组合问题
            from itertools import combinations
            comb = combinations(user_attention, 2)
            # 共同关注的人
            common_user = set()

            for item in comb:
                common_user.update(self.conn.sinter(item))
            #     返回共同关注的信息
            # 移除用户本人
            # common_user.remove(f'{pk}'.encode('utf8'))
            # 找到用户未关注的
            # 求出差集(包括移除本人
            return self.queryset.filter(pk__in=common_user.difference(user_attention))
        elif value == 'pop':
            """都在关注"""
            # for user in queryset:
            #     # 获取成员大小
            #     attention_size = self.conn.scard(user.pk)
            #     if attention_size > 5:
            #         pass

            pass
            # self.queryset()
        return queryset


class CustomRecordFilter(filters.FilterSet):
    type = filters.CharFilter(method="type_filter")

    class Meta:
        model = CustomRecord  # 模型名
        fields = ['type']

    def type_filter(self, queryset, name, value):
        return queryset.filter(status=value)


class StimulateGoodsFilter(filters.FilterSet):
    class Meta:
        model = StimulateModel  # 模型名
        fields = ['type']
