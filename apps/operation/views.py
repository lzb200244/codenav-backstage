from django.db.models import F
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from rest_framework.mixins import CreateModelMixin
from rest_framework.mixins import ListModelMixin, UpdateModelMixin
from rest_framework.generics import GenericAPIView
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView
from apps.account.models import SiteData, SiteDataUser, UserDetail, UserInfo, Type, Categories
from apps.account.views import BaseView
from apps.operation.filters import SiteDataFilter
from apps.operation.models import Comments, Images, News, Inform
from apps.operation.serializers import RecommendSerializer, ReplySerializer, SiteDetailSerializers, NewsSerializers
from utils.GetSiteDetail import GetSiteDetail
from utils.Tencent.sendemial import SENDEMAIL
from utils.response_status import APIResponse
from utils.Tencent.cos import tencent
from utils.auth.loginAuth import LoginAuth
from utils.makeWordCloud.makeWordCloud import MakeWord
from utils.md5 import make_uuid
from utils.pagination import MyPagination
from utils.CountWord import CountWord
from utils.workshop.ReFactory import Pattern


class AllSelects(APIView):
    """所有的选项"""

    def get(self, request):
        inform_choices = Inform.MESSAGE_TYPE
        choices = dict(Type.TYPE_CHOICES)
        dicts = {v: [] for k, v in choices.items()}
        select_list = []
        for item in Categories.objects.values("categories", 'type__type', 'pk'):
            dic_item = {'label': item['categories'], 'value': item['pk']}
            select_list.append(dic_item)
            dicts[choices.get(item['type__type'])].append(dic_item)
        choices = dict(Images.TYPE_CHOICES)

        img = {
            v: [] for k, v in choices.items()
        }
        for item in Images.objects.values("path", 'type'):
            img[choices.get(item['type'])].append(item['path'])
        response_dict = {'select': dicts, 'img': img, 'selectList': select_list, 'inform': inform_choices}

        return APIResponse(response_dict)


class SiteListView(BaseView, ListModelMixin, GenericAPIView):
    """ok"""
    """返回全部数据"""
    queryset = SiteData.objects.all()
    throttle_classes = [AnonRateThrottle, ]  # 限流
    serializer_class = RecommendSerializer  # 序列化器
    pagination_class = MyPagination  # 分页器
    filter_class = SiteDataFilter  # 过滤器

    def filter_queryset(self, queryset):
        """过滤"""
        filter = self.filter_class(data=self.request.data,
                                   queryset=self.queryset, request=self.request)
        return filter.qs

    def paginate_queryset(self, queryset):
        if self.paginator is None:
            return None
        # query_params的值===self.request.data
        self.request.query_params._mutable = True
        self.request.query_params.update(
            self.request.data
        )
        return self.paginator.paginate_queryset(queryset, self.request, view=self)

    def post(self, request):
        """修改get未post但是还是使用list方法"""

        return APIResponse(self.list(request).data)


class SiteDetailView(BaseView, ListModelMixin, GenericAPIView):
    """单独页面详细"""
    throttle_classes = [AnonRateThrottle, ]
    serializer_class = SiteDetailSerializers  # 序列化器

    def get_serializer(self, *args, **kwargs):
        return self.serializer_class(self.queryset, context={'request': self.request})

    def get_queryset(self):
        uid = self.request.query_params.get('uid')
        query = SiteData.objects.filter(uid=uid)
        if query.exists():
            self.queryset = query.first()
            return self.queryset

    def get(self, request):
        return APIResponse(self.list(request).data)


class HandleUserOperation(BaseView, UpdateModelMixin, GenericAPIView, ):
    """处理用户对数据操作"""
    queryset = SiteData.objects.all()
    serializer_class = RecommendSerializer
    authentication_classes = [LoginAuth, ]

    def post(self, request):
        """评论区操作"""
        status = str(request.data.get("status"))
        uid = request.data.get("uid")
        id = request.data.get("id")
        value = request.data.get("value")
        instance = SiteDataUser.objects.filter(sitedata__uid=uid, user=request.user).first()
        site_obj = SiteData.objects.filter(uid=uid)
        if id:
            instance = Comments.objects.filter(id=str(id))
            if not instance.exists(): return
            if status == '1':
                instance.update(like=F('like') + 1)
            elif status == '2':
                instance.update(like=F('like') - 1)
            if status == '3':
                value = request.data.get("value")
                site_obj = SiteData.objects.filter(uid=uid)
                site_obj.update(rating=F('rating') + float(value))
                site_obj = site_obj.first()
                site_user_obj = SiteDataUser.objects.filter(user=request.user_obj.user,
                                                            sitedata=site_obj).first()
                site_user_obj.rated = True
                site_user_obj.save()
        else:
            # 评分该网站
            if value:
                site_obj.update(rating=F('rating') + value)
                instance.rated = True
                instance.rating = value
                instance.save()

        return APIResponse(data='', msg='success', code=1000)

    def put(self, request):
        """收藏取消"""
        status = request.data.get("status")
        uid = request.data.get("uid")
        # 获取当前用户点击的对象
        site_obj = SiteData.objects.filter(uid=uid)
        # 获取当前与用户绑定的点击对象
        instance = SiteDataUser.objects.filter(sitedata__uid=uid, user=request.user).first()
        if all([status, instance]):
            # 先判断当前对象是否存在
            site_obj.update(collect_num=F('collect_num') - 1)
            self.code = 401
            if instance:
                rating = instance.rating
                site_obj.update(rating=F('rating') - rating)
                instance.delete()
                self.code = 200
        if not status and not instance:
            # 判断当前对象是否存在
            user_obj = UserDetail.objects.filter(id=request.user.pk, ).first()
            site_obj.update(collect_num=F('collect_num') + 1)
            # raise ValueError
            SiteDataUser.objects.create(user_id=user_obj.pk, sitedata=site_obj.first(), star=True)

        return APIResponse('', code=self.code)


class ReplyView(BaseView, ListModelMixin, CreateModelMixin, GenericAPIView):
    """评论视图类"""

    serializer_class = ReplySerializer
    authentication_classes = [LoginAuth, ]
    queryset = Comments.objects.all()

    def get_queryset(self):
        print(self.request.query_params.get("uid"))
        uid = self.request.query_params.get("uid").split('?')[0]
        return self.queryset.filter(reply_site_id=uid).order_by("-create_datetime")

    def get(self, request):
        """获取评论列表"""
        return APIResponse(self.list(request).data)

    def get_serializer(self, *args, **kwargs):
        request = self.request
        if request.method == 'GET':
            return super(ReplyView, self).get_serializer(self.get_queryset(), many=True)
        return self.serializer_class(data=request.data, context={'request': request})

    def post(self, request):
        """用户评论"""
        return APIResponse(self.create(request).data)

    def delete(self, request):
        pass


class NewsView(ListModelMixin, GenericAPIView):
    """网站日程"""
    serializer_class = NewsSerializers
    queryset = News.objects.all()

    def get(self, request):
        return APIResponse(self.list(request).data)


@csrf_exempt
def save_file(request):
    """图片上传"""
    try:
        file_obj = request.FILES.get("site_img")
        file_obj2 = request.FILES.get("user_img")
        if file_obj:
            ext = file_obj.name.rsplit(".")[-1]
            image_url = tencent.upload_file(local_file_name=file_obj,
                                            file_name=str(make_uuid()) + "." + ext)
        else:
            # //上传头像
            pk = request.POST.get("pk")
            user_obj = UserDetail.objects.filter(userinfo=pk).first()

            ext = file_obj2.name.rsplit(".")[-1]
            image_url = tencent.upload_file(local_file_name=file_obj2,
                                            file_name=str(make_uuid()) + "." + ext,
                                            bucket="userimages-1311013567")
            # 删除原来数据(桶
            get_old = user_obj.userAvatar
            tencent.delete_file(get_old.split("/")[-1])
            user_obj.userAvatar = image_url
            user_obj.save()
    except Exception as e:
        image_url = 0
    return HttpResponse(image_url)


def spider(request):
    try:
        url = request.GET.get("spider_url")
        if not url.startswith("http"):
            obj = GetSiteDetail(site_url="https://" + url)
        else:
            obj = GetSiteDetail(site_url=url)
        return APIResponse(obj.get_site_ico)
    except Exception as e:
        return APIResponse(-1)


class OuterApi(APIView):
    """这应该是个定时任务每天零点删除一次词云"""

    def get(self, request):
        words = [item for item in CountWord.get().items()]
        # 生成词云
        res = MakeWord(words=sorted(words, reverse=True, key=lambda x: x[1])).make()
        # 上传到cos存储
        return APIResponse("success" if res else "error", )


class EmailUtilView(APIView):
    """发送邮箱请求的接口"""

    def post(self, request):
        email = request.data.get("email")
        pattern = Pattern()
        pattern = pattern["email"]
        if not pattern.match(email):
            return APIResponse(**{"code": 401, "msg": "邮箱格式错误"})
        if not UserInfo.objects.filter(email=email).first():
            return APIResponse(**{"code": 401, "msg": "邮箱不存在"})
        res = SENDEMAIL.config(title="CodeMiner-site", msg="", to=email,
                               code='str')
        if not res:
            return APIResponse(**{"code": 401, "msg": "验证码发送失败"})
        return APIResponse(**{"code": 200, "msg": ""})
