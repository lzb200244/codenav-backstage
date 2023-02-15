from django.db import models
from utils.md5 import make_uuid


# 用户表
class UserInfo(models.Model):
    """用户信息"""
    username = models.CharField(max_length=32, verbose_name="账号", help_text="账号")
    password = models.CharField(max_length=32, verbose_name="密码", help_text="密码")
    email = models.CharField(max_length=32, verbose_name="邮箱", help_text="邮箱")
    token = models.CharField(verbose_name="token", blank=True, default=make_uuid(), null=False, max_length=128)
    qqid = models.CharField(verbose_name="腾讯ID", null=True, max_length=128)

    detail = models.OneToOneField(to="UserDetail", on_delete=models.CASCADE)
    join_time = models.DateTimeField(auto_now_add=True, verbose_name="加入日期")

    def save(self, *args, **kwargs):
        # self.password = md5(self.password)
        super(UserInfo, self).save(*args, **kwargs)

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = '用户信息'
        verbose_name_plural = '用户信息'


# 用户详细表
class UserDetail(models.Model):
    """用户详细信息"""
    qq = models.CharField(default="暂无", blank=True, null=True, help_text="QQ号必须唯一", max_length=18)
    name = models.CharField(max_length=32, help_text="请输入昵称", blank=True, null=True, default="勤劳的搬运工")
    habit = models.ManyToManyField(to="Categories", )
    message = models.TextField(default="我来自外太空!", blank=True, null=True)
    WORK_CHOICES = ((1, "学生"),
                    (2, "在职"),
                    (1, "教师"),
                    (1, ""),
                    (1, "学生"),)
    userAvatar = models.CharField(max_length=268, default="key", blank=True, null=True)
    score = models.IntegerField(default=0)

    # user_img = models.ImageField(verbose_name='用户头像', null=True, upload_to='images/', )
    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = '用户详细信息'
        verbose_name_plural = '用户详细信息'


class Type(models.Model):
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

    pass


# 种类表
class Categories(models.Model):
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

class SiteData(models.Model):
    uid = models.UUIDField(auto_created=True, primary_key=True, default=make_uuid().hex)
    site_url = models.CharField(max_length=268, verbose_name="网站地址(必填)", blank=True, )
    name = models.CharField(max_length=32, verbose_name="网站名字(选填)",
                            help_text="选填", blank=True, )
    img_url = models.URLField(default="", verbose_name="腾讯cos图片url", blank=True, help_text="上传图片")
    collect_num = models.IntegerField(null=True, blank=True, default=0, verbose_name="收藏数量")
    introduce = models.TextField(default="", null=True, blank=True, verbose_name="网站介绍(选填)", )
    show = models.IntegerField(verbose_name="点击数量", default=0)
    VALID_CHOICES = (
        (1, "审核中"),
        (2, "未通过审核"),
        (3, "通过审核"),
    )
    isvalid = models.PositiveIntegerField(choices=VALID_CHOICES, default=1, verbose_name='是否通过审核')

    update_time = models.DateTimeField(verbose_name="上传日期", auto_now_add=True, blank=True, )
    datatype = models.ManyToManyField(to=Categories, verbose_name="类型")
    recommend = models.ForeignKey(to=UserInfo, on_delete=models.CASCADE, related_name="recommend",
                                  verbose_name="推荐人", null=True, blank=True)
    sitedatauser = models.ManyToManyField(to=UserInfo, through="SiteDataUser", related_name="sitedatauser",
                                          through_fields=("sitedata", "user",))

    rating = models.FloatField(verbose_name="评分", blank=True, default=0)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '网站数据'
        verbose_name_plural = '网站数据'


# 自定义第三张user和sitedata表
class SiteDataUser(models.Model):
    """自定义第三张表与SiteData和User绑定关系"""
    user = models.ForeignKey(verbose_name="参与者", on_delete=models.CASCADE, to="UserInfo", related_name="user")
    sitedata = models.ForeignKey(verbose_name="项目", on_delete=models.CASCADE, to="SiteData",
                                 related_name="sitedata")
    star = models.BooleanField(verbose_name="星标", default=False)
    rating = models.FloatField(default=0)
    rated = models.BooleanField(verbose_name="是否已经评分", default=False)

    def __str__(self):
        return str(self.user) + ":" + str(self.sitedata)


__all__ = [UserInfo, UserDetail, SiteData, Categories, Type]
