"""序列化器"""
import datetime
import json
from django_redis import get_redis_connection
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from apps.operation.models import Inform
from mycelery.mytasks.email.tasks import send_email_to_admin
from utils.cal_week import get_week_key, set_score
from utils.md5 import md5, make_uuid
from apps.account.models import UserInfo, UserDetail, SiteData
from utils.workshop.ReFactory import Pattern

conn = get_redis_connection('hall')


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
        "join_time": instance.create_time.strftime("%Y年%m月%d日"),
        "habit": [
            {"label": str(item.categories), "value": item.pk}
            for item in instance.detail.habit.all()],
        "message": instance.detail.message,
        "other": instance.qqid,
        'score': instance.detail.score

    }


class RegisterSerializer(serializers.ModelSerializer):
    re_password = serializers.CharField(max_length=18, read_only=True)
    username = serializers.CharField(max_length=18, min_length=6, error_messages={
        "max_length": "账号长度应该在6-18",
        "min_length": "账号长度应该在6-18"

    }, required=True)
    password = serializers.CharField(max_length=18, min_length=6, error_messages={
        "max_length": "密码长度应该在6-18",
        "min_length": "密码长度应该在6-18"

    }, required=True)
    email = serializers.EmailField(error_messages={
        'invalid': '邮箱已经存在了',
    }, required=True)

    class Meta:
        model = UserInfo
        fields = ['username', 'email', 'password', 're_password']

    def validate_username(self, value):
        exist = UserInfo.objects.filter(username=str(value)).exists()
        if exist:
            raise ValidationError(detail={"msg": "用户名已存在!"}, code=4000)
        if len(str(value)) < 6:
            raise ValidationError(detail={"msg": "用户名过短!"})

        return value

    def validate_password(self, value):

        return md5(value)

    def validate_email(self, value):

        obj = Pattern()
        if not obj["email"].match(value):
            raise ValidationError(detail={"msg": "邮箱格式不对!"})
        if UserInfo.objects.filter(email=value).exists():
            raise ValidationError(detail={"msg": "邮箱已经存在!"})
        return value

    def validate(self, attrs):

        if md5(self.context['request'].data.get("re_password")) != attrs["password"]:
            raise ValidationError(detail={"msg": "两次密码不一致!"})
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
    score = serializers.SerializerMethodField()

    class Meta:
        model = UserInfo
        fields = "__all__"

    def get_detail(self, instance):
        """处理一对一"""
        conn = get_redis_connection('account')
        request = self.context['request']
        update_list = ['message', 'qq', 'name', 'habit', 'userAvatar']
        for update in update_list:
            # 处理多对多
            if update == 'habit':
                # instance.detail.habit.set(habit)
                instance.detail.habit.set(request.data.get(update, getattr(instance.detail, update).all()))
            else:
                t = request.data.get(update, getattr(instance.detail, update))
                if update == 'userAvatar':
                    conn.set(instance.username, t)
                setattr(instance.detail, update, t)
        instance.detail.save()
        return detail(instance)

    def get_score(self, obj):
        return obj.display_score()


class AccountSerializers(serializers.ModelSerializer):
    detail = serializers.SerializerMethodField()

    isLogin = serializers.SerializerMethodField()
    score = serializers.SerializerMethodField()
    hitCount = serializers.SerializerMethodField()
    follows = serializers.SerializerMethodField()

    class Meta:
        model = UserInfo
        exclude = ['id', 'password', 'qqid']

    def get_follows(self, query):
        """
        返回用户关注者
        :param query:
        :return:
        """
        return conn.smembers(query.pk)

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
        return val.display_score()

    def get_detail(self, instance):
        return detail(instance)

    def get_hitCount(self, instance):
        """返回改该用户的通知总条数"""
        return instance.inform_set.count()


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
        # 耗时操作
        # todo 异步
        # 当前带审核个数
        send_email_to_admin.delay()
        # 加积分
        key = get_week_key()
        conn = get_redis_connection('account')
        set_score(conn, key, 1, user.username)

        instance.save()
        return instance


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


class FollowSerializers(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = UserInfo
        fields = ['user']

    def get_user(self, query):
        #
        # 生成用户关注的人
        # 是否存在互相关注

        return query.make_user_info(self.context['request'].user)
