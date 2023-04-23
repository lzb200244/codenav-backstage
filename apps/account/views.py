"""账户相关"""
import datetime
import copy
from QQLoginTool.QQtool import OAuthQQ
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from apps.account.models import UserInfo, SiteData
from apps.account.serializers import (RegisterSerializer, UserInfoSerializers, AccountSerializers, RecommendSerializers,
                                      InformSerializers)
from apps.operation.models import Inform
from django.conf import settings
from enums.response import CodeResponseEnum, StatusResponseEnum
from extensions.permissions.IsAuthenticated import CustomIsAuthenticated
from utils.md5 import md5, make_uuid
from utils.pagination import MyPagination
from utils.response import APIResponse
from rest_framework.mixins import UpdateModelMixin, ListModelMixin, DestroyModelMixin, CreateModelMixin
from QQLoginTool import QQtool
from rest_framework.exceptions import ValidationError
from django_redis import get_redis_connection
import logging

# redis 连接池
conn = get_redis_connection('account')
# 日志处理
logger = logging.getLogger('account')  #


class BaseView(object):
    data = {}
    msg = ""
    code = 1000
    ResponseId = str(make_uuid())
    status = 200


class Tencent(BaseView, APIView):
    """绑定腾讯qq"""
    permission_classes = [CustomIsAuthenticated]
    qq = OAuthQQ(client_id=settings.QQ_CLIENT_ID, client_secret=settings.QQ_CLIENT_SECRET,
                 redirect_uri="https://codeminer.cn/account/person",
                 state="next")

    def get(self, request):
        """
        get:
         账号注册--获取绑定qq的二维码链接

         获取绑定qq的二维码链接,status: 200(成功),code :1000(成功), return :跳转qq登录链接
        """
        return APIResponse(self.qq.get_qq_url())

    def get_authenticators(self):
        if self.request.method != 'GET':
            return super(Tencent, self).get_authenticators()

    def post(self, request):
        """
        post:
         账号注册--用户绑定回调

         用户绑定qq回调,status: 200(成功),code :1000(成功), return :str
        """
        try:
            token = self.qq.get_access_token(request.data.get("code"))
        except:
            logger.warning('临时凭证过期')
            return APIResponse(data="", code=CodeResponseEnum.NotFound.value, msg='临时凭证过期')
        user_obj = request.user
        user_obj.qqid = self.qq.get_open_id(token)

        user_obj.save()

        return APIResponse(data="success", msg='绑定成功')


class LoginMethod(BaseView):
    def __init__(self, *args, **kwargs):
        self.data = kwargs

    def service_email(self):
        """邮箱登入"""
        user_obj = UserInfo.objects.filter(email=self.data.get("email"))
        if not user_obj.exists():
            self.msg = "邮箱不存在"
            raise ValidationError(detail=self.msg, code=401)
        if conn.get(self.data.get("email")).decode('utf-8') != self.data.get("code"):
            self.msg = "验证码过期或者邮箱错误"
            raise ValidationError(detail=self.msg, code=401)
        return user_obj

    def service_account(self, ):
        """账号登入"""
        user_obj = UserInfo.objects.filter(username=self.data.get("username"),
                                           password=md5(self.data.get("password", "0")))
        if not user_obj.exists():
            self.msg = "用户名或密码错误"
            raise ValidationError(detail=self.msg, code=401)
        return user_obj

    def service_tencent(self, ):
        """qq登录"""
        qq = OAuthQQ(client_id=settings.QQ_CLIENT_ID, client_secret=settings.QQ_CLIENT_SECRET,
                     redirect_uri=settings.QQ_REDIRECT_URI,
                     state="next")
        try:
            token = qq.get_access_token(self.data.get("user_code"))
        except:
            self.msg = "临时凭证过期"
            logger.warning(self.msg)
            raise ValidationError(detail=self.msg)
        if not token:
            self.msg = "非法登录"
            logger.warning(self.msg)
            raise ValidationError(detail=self.msg)
        user_obj = UserInfo.objects.filter(qqid=qq.get_open_id(token))
        if not user_obj.exists():
            self.msg = "此账号未注册"
            logger.info(self.msg)
            raise ValidationError(detail=self.msg)
        return user_obj


class AccountView(BaseView, ListModelMixin, UpdateModelMixin, GenericAPIView):
    """账户视图"""

    qq_obj = QQtool.OAuthQQ()
    serializer_class = AccountSerializers

    def get_serializer(self, *args, **kwargs):
        """
        对不同请求使用序列化器

        """
        request = self.request
        if request.method == 'PUT':
            return UserInfoSerializers(instance=self.request.user, data=request.data,
                                       context={'request': self.request},
                                       partial=True,
                                       )  # 指定partial=True部分校验 instance=对象 data=request.data
        return self.serializer_class(self.queryset)

    def get_object(self):
        """
        获取相当于pk的
        """
        return self.request.user

    # 用户点击个人返回数据
    def get_queryset(self):
        if self.request.method == 'POST':
            return super(AccountView, self).get_queryset()
        self.queryset = self.request.user
        return self.queryset

    def get_authenticators(self):
        if self.request.method in ['POST']:
            return []
        return super(AccountView, self).get_authenticators()

    def get(self, request):

        """

        get:
        用户信息--获取用户个人信息

        返回当前用户对象,status: 200(成功),code :1000(成功), return :query
        """

        return APIResponse(self.list(request).data)

    def post(self, request):

        """登录"""
        data = copy.deepcopy(request.data)
        obj = LoginMethod(**data)
        opt = str(request.data.get('opt'))
        func_map = {
            "1": "email",
            "2": "account",
            "3": "tencent",
        }
        if not hasattr(obj, "service_" + func_map.get(opt)):
            return APIResponse('非法请求', code=self.code)
        try:
            user_obj = getattr(obj, "service_" + func_map.get(opt))()
        except ValidationError as e:

            return APIResponse(msg=e.get_full_details()[0].get("message"),
                               status=StatusResponseEnum.Unauthorized,
                               code=CodeResponseEnum.Unauthorized)
        user_obj = user_obj.first()
        jwt_token = user_obj.get_token()
        return APIResponse({'token': jwt_token}, msg='登入成功')

    def put(self, request, *args, **kwargs):
        """更新个人信息"""
        return APIResponse(self.update(request, *args, **kwargs).data)


class RegisterView(BaseView, APIView):
    """
    注册
    """

    def post(self, request):
        ser_obj = RegisterSerializer(data=request.data, context={'request': request})
        if ser_obj.is_valid():
            ser_obj.save()
            self.msg = "注册成功"
        else:
            data = ser_obj.errors
            self.code = 1101  # 输入账户相关的错误
            self.status = 401
            for k, v in data.items():
                self.msg = v.get('error')
                break  # 循环一次就可以了
        return APIResponse(msg=self.msg, status=self.status, code=self.code)


class InformView(ListModelMixin, DestroyModelMixin, GenericAPIView):
    """个人通知"""
    serializer_class = InformSerializers
    queryset = Inform.objects.all()
    permission_classes = [CustomIsAuthenticated]

    def get_queryset(self):
        picker_timer = self.request.data.get('picker')
        type = self.request.data.get('type')
        query = self.queryset.filter(user=self.request.user, type=type)
        if picker_timer:
            time = datetime.datetime.strptime(picker_timer, '%Y/%m/%d')
            return query.filter(
                create_time__day=time.day,
                create_time__year=time.year,
                create_time__month=time.month,
            )
        return query

    def post(self, request):
        """
        :param :picker 时间筛选
        :param :type 过滤类型=>Inform.MESSAGE_TYPE
        post:

        通知--返回用户通知

        返回用户通知,status:200(成功),return:过滤结果
        """

        return APIResponse(self.list(request).data)

    def get_object(self):
        if self.request.method in ['DELETE']:
            clear = self.request.data.get('clear')
            if clear is True:  # 清空所有
                return self.queryset.filter(user=self.request.user)
            # 清除单独
            pk = self.request.data.get('pk')
            return self.queryset.filter(pk=pk, user=self.request.user)
        super(InformView, self).get_object()

    def delete(self, request):
        """
        :param :clear? 是否清空 =>bool
        :param :pk 清空的对象

        delete:

        通知--用户删除通知
        返回'',status:200(成功),return:过滤结果
        """
        return APIResponse(self.destroy(request).data)


class RecommendListView(ListModelMixin, DestroyModelMixin, CreateModelMixin, GenericAPIView):
    """用户推荐列表"""
    serializer_class = RecommendSerializers
    queryset = SiteData.objects.all()
    pagination_class = MyPagination
    permission_classes = [CustomIsAuthenticated]

    def get_queryset(self):
        """
        按时间展示用户推荐过的

        """
        return SiteData.objects.filter(recommend=self.request.user).order_by('-update_time').all()

    def get_serializer(self, *args, **kwargs):
        """
        对不同的请求序列化
        """
        if self.request.method == 'GET':
            return super(RecommendListView, self).get_serializer(*args, **kwargs)
        return self.serializer_class(data=self.request.data, )

    def get_object(self):
        if self.request.method in ['DELETE', 'PUT']:
            query = self.get_queryset().filter(uid=self.request.data.get('uid'))
            if query.exists():  # 存在就返回
                return query.first()
            return query  # 空对象
        super(RecommendListView, self).get_object()

    def get(self, request):
        """
        :param:page 页码

        get:
         推荐--获取用户推荐

         返回用户推荐过的,status: 200(成功),code :1000(成功), return :query
        """
        return APIResponse(self.list(request).data)

    def post(self, request, *args, **kwargs):
        """

        :param:site_url 地址
        :param:datatype 推荐类型 =>list
        :param:img_url 图片url
        :param:introduce 推荐的原因

        post:
        推荐--用户推荐对象

        返回推荐的对象,status: 200(成功),code :1000(成功), return :query
        """

        return APIResponse(self.create(request, *args, **kwargs).data)

    def put(self, request):
        """

        :param:uid 审核的标识


        put:
        推荐--推荐不过重新发去审核

        返回'',status: 200(成功),code :1000(成功), return :query
        """

        # 重新审核
        instance = self.get_object()
        instance.isvalid = 1
        instance.save()
        return APIResponse(data='success')

    def delete(self, request, ):
        """
        :param:uid 审核的标识

        delete:
        推荐--删除审核不过的

        返回'',status: 200(成功),code :1000(成功), return :query
        """
        """删除"""
        return APIResponse(self.destroy(request).data)
