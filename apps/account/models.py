import jwt
from django.conf import settings
from django.db import models
from django_redis import get_redis_connection
from utils.md5 import make_uuid

# 用户表
from utils.models import BaseModel


class UserInfo(BaseModel):
    """用户信息"""
    username = models.CharField(
        max_length=32,
        unique=True,
        verbose_name='账号'
    )
    password = models.CharField(
        max_length=32,
        verbose_name='密码',
    )
    email = models.EmailField(
        max_length=64,
        unique=True,
        verbose_name='邮箱'
    )
    qqid = models.CharField(
        max_length=128,
        verbose_name='腾讯ID',
        null=True,
        blank=True
    )
    detail = models.OneToOneField(
        to='UserDetail',
        on_delete=models.CASCADE,
        related_name='user_detail'
    )

    def save(self, *args, **kwargs):
        # self.password = md5(self.password)
        super(UserInfo, self).save(*args, **kwargs)

    def __str__(self):
        return self.username

    def make_user_info(self, user=None) -> dict:
        """
        :param creator: UserInfo
        :param user: UserInfo
        :return:
        """
        conn = get_redis_connection('hall')

        """生成用户信息"""
        return {
            'id': self.pk,
            'username': self.detail.name,
            'avatar': self.detail.userAvatar,
            'score': self.detail.score,
            'introduce': self.detail.message,
            'habit': [
                {"label": str(item.categories), "value": item.pk}
                for item in self.detail.habit.all()],
            # 是否存在交集(互相关注

            'cross': conn.sismember(self.pk, user.pk) if user else False
        }

    def display_score(self, ) -> str:
        """
        得分语义化
        :return: 等级
        """
        score = self.detail.score
        if score < 5:
            return '1级搬运工'
        elif score < 10:
            return '2级搬运工'
        elif score < 20:
            return '3级搬运工'
        elif score < 45:
            return '4级搬运工'
        elif score < 60:
            return '5级搬运工'
        elif score < 80:
            return '6级搬运工'
        return ""

    def get_token(self) -> str:
        """
        生成jwt返回给用户
        :return:
        """
        SALT = settings.SECRET_KEY  # 岩

        headers = {
            'typ': settings.JWT_CONF.get('typ', 'jwt'),  # 头
            'alg': settings.JWT_CONF.get('alg', 'HS256'),  # 算法
        }
        payload = {
            'id': self.pk,
            'name': self.username,
            'exp': settings.JWT_CONF.get('exp', 60)
        }

        token = jwt.encode(payload=payload, key=SALT, algorithm=headers.get('alg'), headers=headers).encode(
            "utf-8").decode(
            'utf-8')
        return token

    class Meta:
        verbose_name = '用户信息'
        verbose_name_plural = '用户信息'

    # 用户详细表


class UserDetail(models.Model):
    """用户详细信息"""
    qq = models.CharField(
        max_length=18,
        null=True,
        blank=True,
        help_text='QQ号必须唯一'
    )
    name = models.CharField(
        max_length=32,
        null=True,
        blank=True,
        help_text='请输入昵称',
        default='勤劳的搬运工'
    )
    habit = models.ManyToManyField(to='Categories')
    message = models.TextField(
        null=True,
        blank=True,
        default='我来自外太空!'
    )
    userAvatar = models.CharField(
        max_length=268,
        null=True,
        blank=True,
        default='key'
    )
    score = models.IntegerField(default=0)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = '用户详细信息'
        verbose_name_plural = '用户详细信息'


class Type(BaseModel):
    TYPE_CHOICES = (
        (1, '推荐'),
        (2, '编程语言'),
        (3, '前端'),
        (4, '后端'),
        (5, '面试题'),
        (6, '领域'),
        (7, '资源'),
    )
    type = models.PositiveSmallIntegerField(choices=TYPE_CHOICES, default=1)

    def __str__(self):
        return str(self.get_type_display())


# 种类表
class Categories(BaseModel):
    TYPE_CHOICES = (
        (1, '推荐'),
        (2, '编程语言'),
        (3, '前端'),
        (4, '后端'),
        (5, '面试题'),
        (6, '领域'),
        (7, '资源'),

    )
    categories = models.CharField(
        verbose_name='类型名称', blank=True, null=True, max_length=32)
    type = models.ForeignKey(to=Type,
                             on_delete=models.CASCADE, verbose_name='所属类型')

    def __str__(self):
        return str(self.pk)

    class Meta:
        verbose_name = '类型'
        verbose_name_plural = '类型'


# 资源表

class SiteData(BaseModel):
    uid = models.UUIDField(auto_created=True,
                           primary_key=True, default=make_uuid().hex)
    site_url = models.CharField(max_length=268,
                                verbose_name="网站地址(必填)", blank=True, )
    name = models.CharField(max_length=32,
                            verbose_name="网站名字(选填)",
                            help_text="选填", blank=True, )
    img_url = models.URLField(default="",
                              verbose_name="腾讯cos图片url",
                              blank=True, help_text="上传图片")
    collect_num = models.IntegerField(null=True,
                                      blank=True,
                                      default=0,
                                      verbose_name="收藏数量")
    introduce = models.TextField(
        default="",
        null=True,
        blank=True,
        verbose_name="网站介绍(选填)", )
    show = models.IntegerField(
        verbose_name="点击数量", default=0
    )
    VALID_CHOICES = (
        (1, "审核中"),
        (2, "未通过审核"),
        (3, "通过审核"),
    )
    isvalid = models.PositiveIntegerField(choices=VALID_CHOICES,
                                          default=1,
                                          verbose_name='是否通过审核')

    # update_time = models.DateTimeField(verbose_name="上传日期", auto_now_add=True, blank=True, )
    datatype = models.ManyToManyField(
        to=Categories,
        verbose_name="类型"
    )
    recommend = models.ForeignKey(
        to=UserInfo,
        on_delete=models.CASCADE,
        related_name="recommend",
        verbose_name="推荐人", null=True, blank=True
    )
    sitedatauser = models.ManyToManyField(
        to=UserInfo, through="SiteDataUser",
        related_name="sitedatauser",
        through_fields=("sitedata", "user",)
    )

    rating = models.FloatField(
        verbose_name="评分", blank=True, default=0
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '网站数据'
        verbose_name_plural = '网站数据'


# 自定义第三张user和sitedata表
class SiteDataUser(models.Model):
    """自定义第三张表与SiteData和User绑定关系"""
    user = models.ForeignKey(
        verbose_name="参与者",
        on_delete=models.CASCADE,
        to="UserInfo",
        related_name="user"
    )
    sitedata = models.ForeignKey(
        verbose_name="项目", on_delete=models.CASCADE, to="SiteData",
        related_name="sitedata"
    )
    star = models.BooleanField(
        verbose_name="星标", default=False
    )
    rating = models.FloatField(
        default=0
    )
    rated = models.BooleanField(
        verbose_name="是否已经评分",
        default=False
    )

    def __str__(self):
        return str(self.user) + ":" + str(self.sitedata)


