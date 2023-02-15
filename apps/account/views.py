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
from utils.auth.baseAuth import MyBaseAuth
from utils.auth.loginAuth import LoginAuth
from utils.md5 import md5, make_uuid
from utils.pagination import MyPagination
from utils.redis_pool import REDIS_POOL
from utils.response_status import APIResponse
from rest_framework.mixins import UpdateModelMixin, ListModelMixin, DestroyModelMixin, CreateModelMixin
from QQLoginTool import QQtool
from rest_framework.exceptions import ValidationError

import logging

logger = logging.getLogger('account')  #


class BaseView(object):
    data = {}
    msg = ""
    code = 1000
    ResponseId = str(make_uuid())
    status = 200


class LoginMethod(BaseView):
    def __init__(self, *args, **kwargs):
        self.data = kwargs

    def service_email(self, ):
        """邮箱登入"""
        user_obj = UserInfo.objects.filter(email=self.data.get("email"))
        if not user_obj.exists():
            self.msg = "邮箱不存在"
            raise ValidationError(detail=self.msg, code=401)
        if str(REDIS_POOL.get(self.data.get("email"))) != str(self.data.get("code")):
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


class Tencent(BaseView, APIView):
    """绑定腾讯qq"""
    authentication_classes = [LoginAuth]
    qq = OAuthQQ(client_id=settings.QQ_CLIENT_ID, client_secret=settings.QQ_CLIENT_SECRET,
                 redirect_uri="https://codeminer.cn/account/person",
                 state="next")

    def get(self, request):
        """获取qq二维码"""
        return APIResponse(self.qq.get_qq_url())

    def get_authenticators(self):
        if self.request.method != 'GET':
            return super(Tencent, self).get_authenticators()

    def post(self, request):
        """绑定qq"""
        try:
            token = self.qq.get_access_token(request.data.get("code"))
        except:
            logger.warning('临时凭证过期')
            return APIResponse(data="", code=1000, msg='临时凭证过期')
        user_obj = request.user_obj.user
        user_obj.qqid = self.qq.get_open_id(token)
        user_obj.save()
        return APIResponse(data="success", code=1000, msg='绑定成功')


class RecommendListView(ListModelMixin, DestroyModelMixin, CreateModelMixin, GenericAPIView):
    """用户推荐列表"""
    serializer_class = RecommendSerializers
    queryset = SiteData.objects.all()
    pagination_class = MyPagination
    authentication_classes = [LoginAuth, ]

    def get_queryset(self):

        return SiteData.objects.filter(recommend=self.request.user).order_by('-update_time').all()

    def get_serializer(self, *args, **kwargs):
        if self.request.method == 'GET':
            return super(RecommendListView, self).get_serializer(*args, **kwargs)
        return self.serializer_class(data=self.request.data, context={'request': self.request})

    def get_object(self):
        if self.request.method in ['DELETE', 'PUT']:
            query = self.get_queryset().filter(uid=self.request.data.get('uid'))
            if query.exists():  # 存在就返回
                return query.first()
            return query  # 空对象
        super(RecommendListView, self).get_object()

    def get(self, request):

        """用户推荐记录"""

        return APIResponse(self.list(request).data)

    def post(self, request, *args, **kwargs):
        """用户推荐"""

        return APIResponse(self.create(request, *args, **kwargs).data)

    def put(self, request):
        # 重新审核
        instance = self.get_object()
        instance.isvalid = 1
        instance.save()
        return APIResponse(data='success', code=1000)

    def delete(self, request, ):
        """删除"""
        return APIResponse(self.destroy(request).data)


class AccountView(BaseView, ListModelMixin, UpdateModelMixin, GenericAPIView):
    """账户视图"""

    qq_obj = QQtool.OAuthQQ()
    serializer_class = AccountSerializers
    authentication_classes = [MyBaseAuth, LoginAuth]

    def get_serializer(self, *args, **kwargs):
        request = self.request
        if request.method == 'PUT':
            return UserInfoSerializers(instance=self.request.user, data=request.data,
                                       partial=True,
                                       context={'request': request})  # 指定partial=True部分校验 instance=对象 data=request.data
        return self.serializer_class(self.queryset)

    def get_object(self):
        # 获取相当于pk的
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
        """获取个人信息"""
        return APIResponse(self.list(request).data)

    def post(self, request):
        type_ = str(self.request.data.get("type_"))
        if type_ == "1":
            """注册"""
            ser_obj = RegisterSerializer(data=request.data, context={'request': request})
            if ser_obj.is_valid():
                ser_obj.save()
                data = ser_obj.data
                self.msg = "注册成功"
            else:
                data = ser_obj.errors
                self.code = 1101  # 输入账户相关的错误
                self.status = 401
                for k, v in data.items():
                    self.msg = v.get('error')
                    break  # 循环一次就可以了
            return APIResponse(data, msg=self.msg, status=self.status)
        elif type_ == "2":
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

                return APIResponse(msg=e.get_full_details()[0].get("message"), status=401, code=1201)
            user_obj = user_obj.first()
            token = make_uuid()
            REDIS_POOL.set(str(token), user_obj.id, ex=datetime.timedelta(days=14))
            user_obj.token = str(token)
            user_obj.save()
            return APIResponse({'token': token}, msg='登入成功')

    def put(self, request, *args, **kwargs):
        """更新个人信息"""
        return APIResponse(self.update(request, *args, **kwargs).data)


class InformView(ListModelMixin, DestroyModelMixin, GenericAPIView):
    """个人通知"""
    serializer_class = InformSerializers
    queryset = Inform.objects.all()
    authentication_classes = [LoginAuth]

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
        """返回全部通知记录"""

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
        """用户删除通知"""
        return APIResponse(self.destroy(request).data)


"""
class AccountCode(APIView):
    """
# 极验认证
"""


    def get(self, request):

        user_id = 'test'
        gt = GeetestLib(GEETEST_ID, GEETTEST_KEY)
        status = gt.pre_process(user_id)
        REDIS_POOL.set(gt.GT_STATUS_SESSION_KEY, status)
        REDIS_POOL.set("gt_user_id", user_id)
        response_str = gt.get_response_str()
        return HttpResponse(response_str)

    def post(self, request):
        gt = GeetestLib(GEETEST_ID, GEETTEST_KEY)
        challenge = request.data.get(gt.FN_CHALLENGE, '')
        validate = request.data.get(gt.FN_VALIDATE, '')
        seccode = request.data.get(gt.FN_SECCODE, '')
        status = REDIS_POOL.get(gt.GT_STATUS_SESSION_KEY)
        user_id = REDIS_POOL.get("gt_user_id")
        if status:
            result = gt.success_validate(challenge, validate, seccode, user_id)
        else:
            result = gt.failback_validate(challenge, validate, seccode)
        result = {"status": "success"} if result else {"status": "fail"}

        return HttpResponse(json.dumps(result))
"""
