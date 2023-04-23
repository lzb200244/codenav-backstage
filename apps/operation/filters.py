"""operation过滤器"""
from django.contrib.auth.models import AnonymousUser
from django.db.models import Q
from django_filters import rest_framework as filters
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed

from apps.account.models import SiteData
from utils.CountWord import CountWord


class SiteDataFilter(filters.FilterSet):
    """过滤器"""
    search = filters.CharFilter(method="search_filter")
    filter = filters.CharFilter(method="filter_filter")
    ordering = filters.CharFilter(method='ordering_filter')

    def __init__(self, *args, **kwargs):
        self.request = kwargs.get("request", None)

        super(SiteDataFilter, self).__init__(*args, **kwargs)

    class Meta:
        model = SiteData  # 模型名
        fields = "__all__"

    def search_filter(self, queryset, name, value):
        """搜索框"""
        CountWord(value).set()  # 存储搜索次数redis
        return queryset.filter(
            Q(name__icontains=value) | Q(
                site_url__icontains=value)
        ).all()

    def filter_filter(self, queryset, name, value):
        filter_list = self.request.data.get('filter')
        query = queryset
        if isinstance(filter_list, list):
            for item in filter_list:
                query = query.filter(datatype=item)
        return query

    def ordering_filter(self, queryset, name, value):
        ordering_dict = {
            '热门': 'hot',
            '时间': 'time',
            '评分': 'rating',
            '收藏': 'collect'
        }
        order = ordering_dict.get(value)
        if order == 'time':
            return queryset.order_by('-update_time')
        elif order == 'collect':
            user_obj = self.request.user

            if isinstance(user_obj, AnonymousUser):
                # todo   需要登录
                raise AuthenticationFailed(detail={'msg': '需要登录！！', 'code': 1021}, )
            return queryset.filter(sitedatauser=user_obj)

        elif order == 'rating':
            return queryset.order_by('-rating')
        return queryset
