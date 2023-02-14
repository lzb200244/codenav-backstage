"""序列化器"""
import datetime
import json
from django.db.models import Count
from django_redis import get_redis_connection
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from apps.operation.models import Inform

from django.conf import settings
from utils.Tencent.sendemial import SENDEMAIL
from utils.cal_week import get_week_key, set_score
from utils.md5 import md5, make_uuid
from apps.account.models import UserInfo, UserDetail, SiteData
from utils.workshop.ReFactory import Pattern


def get_rest_seconds():
    """计算距离晚上0.00还有多少秒重置点"""
    now = datetime.datetime.now()
    today_begin = datetime.datetime(now.year, now.month, now.day, 0, 0, 0)
    tomorrow_begin = today_begin + datetime.timedelta(days=1)
    rest_seconds = (tomorrow_begin - now).seconds
    return rest_seconds


def detail(instance):
    return {
        "pk": instance.pk,
        "qq": instance.detail.qq,
        "name": instance.detail.name,
        "userAvatar": instance.detail.userAvatar,
        "join_time": instance.join_time.strftime("%Y年%m月%d日"),
        "habit": [
            {"label": str(item.categories), "value": item.pk}
            for item in instance.detail.habit.all()],
        "message": instance.detail.message,
        "other": instance.qqid,
        'score': instance.detail.score

    }


class RegisterSerializer(serializers.ModelSerializer):
    token = serializers.UUIDField(read_only=True)
    re_password = serializers.CharField(max_length=32, read_only=True)
    detail = serializers.CharField(required=False)

    class Meta:
        model = UserInfo
        fields = "__all__"
        excludes = ["token", "detail"]

    def validate_username(self, value):
        exist = UserInfo.objects.filter(username=str(value)).exists()
        if exist:
            raise ValidationError(detail={"error": "用户名已存在!"})
        if len(str(value)) < 6:
            raise ValidationError(detail={"error": "用户名过短!"})

        return value

    def validate_password(self, value):
        return md5(value)

    def validate_email(self, value):
        obj = Pattern()
        if not obj["email"].match(value):
            raise ValidationError(detail={"error": "邮箱格式不对!"})
        if UserInfo.objects.filter(email=value).exists():
            raise ValidationError(detail={"error": "邮箱已经存在!"})
        return value

    def validate(self, attrs):
        if md5(self.context['request'].data.get("re_password")) != attrs["password"]:
            raise ValidationError(detail={"error": "两次密码不一致!"})
        return attrs

    def create(self, validated_data):
        username = validated_data.get("username")
        email = validated_data.get("email")
        password = validated_data.get("password")
        detail = UserDetail.objects.create(name="勤劳的" + username, )
        user_obj = UserInfo.objects.create(username=username, password=password, detail=detail, email=email)
        return user_obj


class UserInfoSerializers(serializers.ModelSerializer):
    detail = serializers.SerializerMethodField()
    score = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = UserInfo
        fields = "__all__"

    def get_detail(self, instance):
        """处理一对一"""
        conn = get_redis_connection('account')
        request = self.context['request']
        qq = request.data.get("qq") if request.data.get("qq") else instance.detail.qq
        name = request.data.get("name") if request.data.get("name") else instance.detail.name
        habit = request.data.get("habit") if request.data.get("habit") else []
        userAvatar = request.data.get("userAvatar") if request.data.get(
            "userAvatar") else instance.detail.userAvatar
        # 更新redis关联的头像 默认没有头像
        conn.set(instance.username, userAvatar)

        message = request.data.get("message") if request.data.get("message") else instance.detail.message
        instance.detail.qq = qq
        instance.detail.name = name
        instance.detail.userAvatar = userAvatar
        instance.detail.habit.set(habit)
        instance.detail.message = message
        instance.detail.save()
        return detail(instance)

    def get_score(self, obj):
        score = obj.detail.score
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


class AccountSerializers(serializers.ModelSerializer):
    detail = serializers.SerializerMethodField(read_only=True)
    isvalid = serializers.SerializerMethodField(read_only=True)
    isLogin = serializers.SerializerMethodField(read_only=True)
    score = serializers.SerializerMethodField(read_only=True)
    hitCount = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = UserInfo
        fields = "__all__"
        excludes = ['id', 'token', 'password', 'qqid']

    def get_isLogin(self, val):
        conn = get_redis_connection('account')
        username = str(val.username)
        if not conn.get(f'login:{username}'):  # 查看是否今天已经登入
            conn.set(f'login:{username}', json.dumps(True), ex=get_rest_seconds())

            key = get_week_key()
            # 存储积分
            set_score(conn, key, 1, username)

            val.detail.score += 1
            val.detail.save()
            return False  # 第一次登录
        return True

    def get_score(self, val):
        score = val.detail.score
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

    def get_isvalid(self, val):
        return val.token

    def get_detail(self, instance):
        return detail(instance)

    def get_hitCount(self, instance):
        """返回改该用户的通知总条数"""
        return instance.inform_set.count()
        pass


class RecommendSerializers(serializers.ModelSerializer):
    """
    用户推荐序列化
    """
    isvalid = serializers.SerializerMethodField()
    datatype = serializers.SerializerMethodField()

    class Meta:
        model = SiteData
        fields = ['uid', 'name', 'site_url', 'img_url', 'datatype', 'introduce', 'isvalid']

    def get_datatype(self, query):
        """修改返回形式"""
        return [item.categories for item in query.datatype.all()]

    def get_isvalid(self, query):
        return query.get_isvalid_display()

    def create(self, validated_data):
        request = self.context['request']
        user = request.user
        instance = SiteData.objects.create(uid=make_uuid().hex, recommend=user,
                                           **validated_data)
        datatype = request.data.get('datatype')
        if isinstance(datatype, list):
            instance.datatype.set(datatype)
            # 当前带审核个数
        check_count = SiteData.objects.filter(isvalid=1).aggregate(check_count=Count("uid"))
        """放入任务队列发送邮箱给管理员"""
        SENDEMAIL.config("CodeMiner-site", to=settings.ADMIN_EMAIL,
                         msg="有用户推荐新资源,当前待审核资源为:%s,你可以点击前往过审%s" % (
                             check_count.get("check_count"),
                             "http://43.138.105.186:8888/codeminer-admin/#/codeminer-admin/account/sitedata/"
                         ))
        # 加积分
        key = get_week_key()
        conn = get_redis_connection('account')
        set_score(conn, key, 1, user.username)

        instance.save()
        return instance
        # SiteData.objects.create(validated_data)


class InformSerializers(serializers.ModelSerializer):
    """
        用户通知
    """
    create_time = serializers.SerializerMethodField(read_only=True)
    type = serializers.CharField(source='get_type_display')
    leave = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Inform
        fields = ['pk', 'type', 'create_time', 'content', 'leave']

    def get_create_time(self, obj):
        return obj.create_time.strftime("%Y年%m月%d日")

    def get_leave(self, obj):
        type_map = {
            '1': 'success',
            '2': 'success',
            '3': '',
            '4': 'error',
            '5': 'warning',
        }
        return type_map.get(str(obj.type))
