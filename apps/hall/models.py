from django.db import models

# Create your models here.
from apps.account.models import UserInfo

from utils.models import BaseModel


class ChatModel(BaseModel):
    ISSUE_CHOICES = (
        (1, "问答"),
        (2, '需求'),
        (3, 'bug'),
        (4, '聊天'),
    )
    title = models.CharField(max_length=32, verbose_name="标题", null=True, blank=True)
    content = models.TextField(verbose_name="内容", null=True, blank=True)
    creator = models.ForeignKey(to=UserInfo, on_delete=models.CASCADE, verbose_name='创建者')
    issue_type = models.PositiveSmallIntegerField(choices=ISSUE_CHOICES, null=True, blank=True)
    replay = models.ForeignKey(to='self', on_delete=models.CASCADE, verbose_name='父评论', null=True, blank=True)
    like = models.IntegerField(default=0, blank=True, null=True, verbose_name='点赞数量')

    def __str__(self):
        return str(self.title)

    @staticmethod
    def make_replays(queryset):
        user_obj = queryset.creator
        comment = {
            'id': queryset.id, 'content': queryset.content, 'replays': [],
            'user': user_obj.make_user_info(user_obj),
            "like": queryset.like,
            "create_time": queryset.create_time.strftime("%Y-%m-%d %H:%M"),
        }
        # 遍历每一个
        for query in ChatModel.objects.all():
            if query.replay_id == queryset.id:
                # 放入子
                #         开是递归
                comment['replays'].append(ChatModel.make_replays(query))
        return comment


class StimulateModel(BaseModel):
    """奖的兑换"""
    TYPECHOICES = (
        (1, '书籍'),
        (2, '会员'),
        (3, '其他'),
    )
    title = models.CharField(max_length=32, verbose_name="奖品名称")
    price = models.IntegerField(verbose_name="价格")
    store = models.IntegerField(verbose_name='库存')
    type = models.PositiveSmallIntegerField(choices=TYPECHOICES, default=1)
    img = models.URLField(verbose_name='照片')


class CustomRecord(BaseModel):
    STATUSCHOICES = (
        (1, "未支付"),
        (2, "已支付"),
        (3, "未发货"),
        (4, "已发货"),
        (5, "已收货"),
    )
    """消费记录"""
    uid = models.UUIDField(auto_created=True, primary_key=True, )
    goods = models.ForeignKey(to=StimulateModel, on_delete=models.CASCADE, verbose_name="商品")
    customer = models.ForeignKey(to=UserInfo, on_delete=models.CASCADE, verbose_name="消费者")
    count = models.IntegerField(verbose_name='数量')
    amount = models.IntegerField(verbose_name="总消费")
    cause = models.CharField(max_length=64, verbose_name='购买失败原因', null=True, blank=True)
    status = models.PositiveSmallIntegerField(
        choices=STATUSCHOICES, default=1
    )
