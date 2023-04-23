from django.db import models

from utils.models import BaseModel


# 评论表
class Comments(BaseModel):
    """评论的对象表"""
    content = models.TextField(verbose_name="评论内容")
    reply_site = models.ForeignKey(to="account.SiteData", on_delete=models.CASCADE, verbose_name="评论的对象",
                                   related_name="reply_site")
    creator = models.ForeignKey(to="account.UserInfo", on_delete=models.CASCADE, verbose_name="评论者",
                                related_name="creator")
    parentId = models.ForeignKey(to="self", on_delete=models.CASCADE, verbose_name="父id", null=True, blank=True, )

    like = models.IntegerField(default=0, blank=True, null=True, verbose_name='点赞数量')

    def __str__(self):
        return str(self.creator.username) + ":" + str(self.content)

    class Meta:
        verbose_name = '评论'
        verbose_name_plural = '评论'


class Images(BaseModel):
    """本站图库"""
    path = models.CharField(max_length=256, verbose_name='图片地址',
                            default='https://cube.elemecdn.com/e/fd/0fc7d20532fdaf769a25683617711png.png')
    TYPE_CHOICES = (
        (1, 'avatar'),
        (2, 'siteImg'),
        (3, 'other')
    )
    type = models.PositiveSmallIntegerField(verbose_name='类别', default=1, choices=TYPE_CHOICES)

    class Meta:
        verbose_name = '图库'
        verbose_name_plural = verbose_name


class Inform(BaseModel):
    """个人通知"""
    MESSAGE_TYPE = (
        (1, '积分消费'),
        (2, '推荐消息'),
        (3, '评论回复'),
        (4, '违规警告'),
        (5, '其他')
    )
    type = models.PositiveSmallIntegerField(choices=MESSAGE_TYPE)
    user = models.ForeignKey('account.UserInfo', on_delete=models.CASCADE, verbose_name='关联用户')
    content = models.TextField(verbose_name='通知内容', null=True, blank=True)

    def __str__(self):
        return f'{self.user.username}:{self.get_type_display()}'

    def save(self, **kwargs):
        """最多存储30条每个人"""
        query = Inform.objects.filter(user=self.user)
        if query.count() == 60:
            """按时间删除"""
            query.order_by('create_time').first().delete()
        super(Inform, self).save(kwargs)

    class Meta:
        verbose_name = '通知'
        verbose_name_plural = '通知'


class News(BaseModel):
    """网站近期更新"""
    title = models.CharField(max_length=32, verbose_name='标题')
    content = models.CharField(max_length=64, verbose_name='更新内容')
    UPDATE_CHOICES = (
        (1, 'primary'),
        (2, 'success'),
        (3, 'warning'),
        (4, 'info')
    )
    type = models.PositiveSmallIntegerField(verbose_name='更新类型', default=2, choices=UPDATE_CHOICES)
    COLOR_CHOICES = (
        (1, '#0bbd87'),
        (2, '#1E90FF'),
        (3, '#FF8C00'),
        (4, '#D3D3D3'),
        (5, '#FFB6C1'),
    )
    color = models.PositiveSmallIntegerField(verbose_name='颜色', default=1, choices=COLOR_CHOICES)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = '网站日程'
        verbose_name_plural = verbose_name


class BillBoard(BaseModel):
    title = models.CharField(max_length=32, verbose_name='标题')
    introduce = models.TextField(verbose_name='内容')
    img = models.URLField(verbose_name='图片')
    link = models.URLField(verbose_name='链接')
