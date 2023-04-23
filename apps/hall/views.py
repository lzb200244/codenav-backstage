import datetime

from uuid import uuid4

from django.db import transaction
from django.db.models import Q
from django.http import Http404
from django_redis import get_redis_connection
from rest_framework.generics import GenericAPIView, get_object_or_404
from apps.account.models import UserInfo, UserDetail
from apps.account.serializers import FollowSerializers
from apps.hall.filters import ChatFilter, CircleFilter, CustomRecordFilter, StimulateGoodsFilter
from apps.hall.models import ChatModel, StimulateModel, CustomRecord
from apps.hall.serializers import ChatSerializers, StimulateGoodsSerializers, CustomRecordSerializers
from extensions.permissions.IsAuthenticated import CustomIsAuthenticated
from utils.cal_week import get_week_key
from utils.mixins.redis import CatchWithRedisMixin
from utils.response import APIResponse
from rest_framework.mixins import ListModelMixin, UpdateModelMixin


class RankView(CatchWithRedisMixin, GenericAPIView):
    """排名"""
    conn_slot = 'account'
    permission_classes = [CustomIsAuthenticated]

    def get_con(self):
        return get_redis_connection(self.conn_slot)

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

    def get_permissions(self):
        if self.request.method == 'POST':
            return []
        return super(RankView, self).get_permissions()

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


class CircleView(CatchWithRedisMixin, ListModelMixin, GenericAPIView):
    """
       社交圈
       """
    conn_slot = 'hall'
    permission_classes = [CustomIsAuthenticated]
    serializer_class = FollowSerializers
    filter_class = CircleFilter  # 过滤器

    def filter_queryset(self, queryset):
        """过滤"""

        filter = self.filter_class(
            conn=self.conn,
            data=self.request.query_params,
            queryset=self.get_queryset(),
            request=self.request,
        )

        return filter.qs

    def get_con(self):
        return get_redis_connection(self.conn_slot)

    def get(self, request):

        type = request.query_params.get('type')
        if type == "common":
            """共同关注"""
            # 用户关注的人
            user_attention = self.conn.smembers(request.user.pk)

            # 只要有大于2的就是说明共同关注(todo 组合问题
            from itertools import combinations
            comb = combinations(user_attention, 2)
            # 共同关注的人
            common_user = set()
            for item in comb:
                common_user.update(self.conn.sinter(item))
            for user_id in common_user:
                pass

        return APIResponse(data=self.list(request).data)

    def get_queryset(self):
        # 获取出了自己的用户
        return UserInfo.objects.filter(~Q(pk=self.request.user.pk))

    def post(self, request):
        status = request.data.get('status')
        follower_id = request.data.get('follow', 0)
        user_id = self.request.user.pk
        cross = False
        if not follower_id:
            return APIResponse(status=401)
        if status:
            # 取消关注
            self.conn.srem(user_id, follower_id)
        else:
            # 关注
            self.conn.sadd(user_id, follower_id)
            # 查看是否是互关
            # SISMEMBER
            # sismember
            cross = self.conn.sismember(follower_id, user_id)

        return APIResponse('success')


class ChatSView(ListModelMixin, GenericAPIView, UpdateModelMixin):
    """
    聊天
    """
    serializer_class = ChatSerializers
    queryset = ChatModel.objects.all()
    permission_classes = [CustomIsAuthenticated]
    filter_class = ChatFilter  # 过滤器

    def filter_queryset(self, queryset):
        """过滤"""
        filter = self.filter_class(
            data=self.request.query_params,
            queryset=self.get_queryset()
        )
        return filter.qs

    def get_queryset(self):
        # 过滤掉回复的
        return ChatModel.objects.filter(replay_id__isnull=True)

    def get(self, request):
        """
        返回评论列表
        :param request:
        :return:
        """
        # 存在id就是说明是获取所有子评论
        chatId = self.request.query_params.get('chatId')
        if chatId:
            try:
                query_obj = get_object_or_404(queryset=self.queryset, id=chatId)
                return APIResponse(ChatModel.make_replays(queryset=query_obj, ))
            except Http404:
                return APIResponse(code=1204, status=404, msg="404")
        # 返回全部评论
        return APIResponse(self.list(request).data)

    def post(self, request):
        """
        提交评论
        :param request:
        :return:
        """
        obj = {}
        obj.update({'creator': request.user}, **self.request.data)
        query = ChatModel.objects.create(**obj)

        comment = {
            'id': query.pk,
            'user': query.creator.make_user_info(request.user)
        }
        return APIResponse(data=comment)

    def get_object(self):
        """
        如果put处理点赞
        :return:
        """
        if self.request.method == "PUT":
            return self.queryset.filter(pk=self.request.data.get('id')).first()
        return super().get_object()

    def put(self, request):
        """
        处理点赞
        :param request:
        :return:
        """
        return APIResponse(self.update(request).data)


class StimulateGoodsView(ListModelMixin, GenericAPIView):
    """激励"""
    serializer_class = StimulateGoodsSerializers
    queryset = StimulateModel.objects.all()
    permission_classes = [CustomIsAuthenticated]
    filter_class = StimulateGoodsFilter

    def filter_queryset(self, queryset):
        filter = self.filter_class(
            data=self.request.query_params,
            queryset=self.get_queryset()
        )
        return filter.qs

    def get(self, request):
        return APIResponse(self.list(request).data)

    def post(self, request):
        """用户对兑换奖励"""

        with transaction.atomic():
            # 开启事务
            good_id = request.data.get('id')
            count = request.data.get('count', 1)
            # 行锁
            query = self.queryset.select_for_update().get(pk=good_id)
            user = UserDetail.objects.select_for_update().get(userinfo=request.user)
            # 总金额
            amount = count * query.price
            # 生成订单记录
            record = CustomRecord.objects.create(
                uid=uuid4().hex,
                goods=query, customer=self.request.user,
                count=count, amount=0, status=1
            )
            # 查看是否够钱
            if user.score <= amount:
                cause = "积分不足,请继续攒"
                record.cause = cause
                record.save()
                return APIResponse(msg=cause, code=1200, data=0)
            if query.store - count < 0:
                # 记录日志
                cause = "库存不足"
                return APIResponse(msg=cause, code=1200, data=0)
            # 库存-1
            query.store -= 1
            # 订单更新=>已支付,支付金额更新
            record.status = 2
            record.amount = amount
            # 用户扣款
            user.score -= amount
            record.save()
            user.save()
            query.save()
        return APIResponse(data=1, msg='兑换成功')


class CustomRecordView(ListModelMixin, GenericAPIView):
    """订单记录"""
    permission_classes = [CustomIsAuthenticated]
    serializer_class = CustomRecordSerializers
    queryset = CustomRecord.objects.all()
    filter_class = CustomRecordFilter

    def filter_queryset(self, queryset):
        filter = self.filter_class(
            data=self.request.query_params,
            queryset=self.get_queryset()
        )
        return filter.qs

    def get(self, request):
        return APIResponse(self.list(request).data)

    def get_queryset(self):
        return self.queryset.filter(customer=self.request.user)
