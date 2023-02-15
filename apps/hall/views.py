import datetime
from django_filters.rest_framework import DjangoFilterBackend
from django_redis import get_redis_connection
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.hall.filters import UserFilter
from utils.auth.loginAuth import LoginAuth
from utils.cal_week import get_week_key
from utils.response_status import APIResponse


class Test(APIView):
    filter_backends = (DjangoFilterBackend,)
    filter_class = UserFilter  # 指定过滤器类
    # 过滤字段
    filter_fields = ['username', ]

    def get(self, request):
        return Response("ok")


class RankView(GenericAPIView):
    """排名"""

    def __init__(self, *args, **kwargs):
        self.conn = get_redis_connection('account')
        super(RankView, self).__init__(*args, **kwargs)

    def rank(self, rank_list, conn):

        rank = []
        for name, score in rank_list:
            rank.append(
                {
                    'name': name,
                    'avatar': conn.get(name),
                    'score': score
                }
            )
        return rank

    def get(self, request):
        """查询排名"""
        tp = request.data.get('tp', 2)
        tp_mp = {
            1: get_week_key(),
            2: 'rank'
        }

        rank = self.conn.zrevrank(tp_mp.get(tp), self.request.user.username)
        if rank is not None:
            rank = rank + 1
        return APIResponse(rank)

    def get_authenticators(self):
        if self.request.method in ['GET']:
            return [LoginAuth()]
        return super(RankView, self).get_authenticators()

    def post(self, request):
        # 总与周
        tp = request.data.get('tp', 2)
        week = request.data.get('week')
        rank = []
        conn = self.conn
        conf = {
            'desc': True, 'withscores': True
        }
        if tp == 1:  # 周排序
            if week:
                week = datetime.datetime.strptime(week, '%Y/%m/%d') + datetime.timedelta(days=1)
            key = get_week_key(week)
            week_rank = conn.zrange(key, 0, 10, **conf)
            rank = self.rank(week_rank, conn)
        elif tp == 2:  # 总排序
            # 总排名
            total_ranks = conn.zrange('rank', 0, -1, **conf)
            rank = self.rank(total_ranks, conn)
        return APIResponse(data=rank)
