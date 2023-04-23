import datetime
import logging
from django.db.models import F
from rest_framework.exceptions import NotFound
from rest_framework.mixins import CreateModelMixin
from rest_framework.mixins import ListModelMixin, UpdateModelMixin
from rest_framework.generics import GenericAPIView
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView
from rest_framework_extensions.cache.decorators import cache_response
from apps.account.models import SiteData, SiteDataUser, UserDetail, UserInfo, Type, Categories
from apps.account.views import BaseView
from apps.hall.models import ChatModel, CustomRecord, StimulateModel
from apps.operation.filters import SiteDataFilter
from apps.operation.models import Comments, Images, News, Inform, BillBoard
from apps.operation.serializers import RecommendSerializer, ReplySerializer, SiteDetailSerializers, NewsSerializers
from extensions.permissions.IsAuthenticated import CustomIsAuthenticated
from mycelery.mytasks.email.tasks import send_user_email

from utils.GetSiteDetail import GetSiteDetail
from utils.response import APIResponse
from utils.Tencent.cos import tencent
from utils.md5 import make_uuid
from utils.pagination import MyPagination
from utils.workshop.ReFactory import Pattern

logger = logging.getLogger('operation')


class AllSelects(APIView):

    # 缓存7天
    @cache_response(timeout=datetime.timedelta(days=7).days, cache='catch')
    def get(self, request):

        """

        get:
         站内所有选项--站内所有选项

        返回站内所有选项如果存在缓存直接从缓存读取且未被修改,status: 200(成功) ,return: 所有选项

        """
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

        response_dict = {
            'select': dicts,
            'img': img,
            'selectList': select_list,
            'inform': inform_choices,
            'HallSelect': {
                'chat': [{'label': item, 'value': index} for index, item in ChatModel.ISSUE_CHOICES],
                'order': [{'label': item, 'value': index} for index, item in CustomRecord.STATUSCHOICES],
                'stimulate': [{'label': item, 'value': index} for index, item in StimulateModel.TYPECHOICES],
            }
        }

        return APIResponse(response_dict, )


class BillBoardView(APIView):
    """"""

    @cache_response(timeout=datetime.timedelta(days=7).days, cache='catch')
    def get(self, request):
        """
        get:
         网站静态面板--个人信息,与简介

         个人信息,与简介存在读取缓存,status: 200(成功) ,return:

        """
        author = billboard = {}
        user_obj = UserInfo.objects.filter(username=200244)
        if user_obj.exists():
            user_obj = user_obj.first()
            author = {
                'qq': user_obj.detail.qq,
                'name': user_obj.detail.name,
                'introduce': user_obj.detail.message,
                'img': user_obj.detail.userAvatar,
                'shape': 'circle',
            }
        board = BillBoard.objects.order_by('update_time')

        if board.exists():
            board = board.first()
            billboard = {
                'title': board.title,
                'link': board.link,
                'introduce': board.introduce,
                'img': board.img,
                'shape': 'square',
            }
        return APIResponse({'author': author, 'board': billboard})


class ImageUpdateView(APIView):
    permission_classes = [CustomIsAuthenticated]

    def post(self, request):
        """图片上传"""

        try:
            code = 1000
            file_obj = request.FILES.get("site_img")
            file_obj2 = request.FILES.get("user_img")
            if file_obj:
                # 上次推荐图片
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
            code = 1200
            image_url = 'https://www.codeminer.cn/siteico.png'
        #     返回图片地址
        return APIResponse(image_url, code=code)


class SiteListView(BaseView, ListModelMixin, GenericAPIView):
    queryset = SiteData.objects.all()
    throttle_classes = [AnonRateThrottle, ]  # 限流
    serializer_class = RecommendSerializer  # 序列化器
    pagination_class = MyPagination  # 分页器
    filter_class = SiteDataFilter  # 过滤器

    def filter_queryset(self, queryset):
        """
        过滤
        """
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
        # print(request.user)
        """
        :param:ordering 排序方式 default:
        :param:page 页码 default:
        :param:search? 搜索框按过滤
        :param:filter? 过滤多项    ->type:list
        post:
        站内列表--返回站内的所有资源

        返回过滤后的数据, status:200 (成功)

        """
        return APIResponse(self.list(request).data)


class SiteDetailView(BaseView, ListModelMixin, GenericAPIView):
    """单独页面详细"""
    throttle_classes = [AnonRateThrottle, ]

    serializer_class = SiteDetailSerializers  # 序列化器

    def get_serializer(self, *args, **kwargs):
        request = self.request
        return SiteDetailSerializers(
            context={'request': request},
            instance=self.queryset
        )

    def get_queryset(self):
        uid = self.request.query_params.get('uid')
        try:
            self.queryset = SiteData.objects.get(uid=uid)
        except SiteData.DoesNotExist:
            raise NotFound({'msg': '页面走丢了！！', 'code': 1024})
        return self.queryset

    def get(self, request):
        """
        :param : uid 请求标识

        get
         详细页面--获取单页面详细内容

         返回单独页面信息,status: 200(成功),return :单独对象

        """
        return APIResponse(self.list(request).data)


class SiteDataOperation(BaseView, UpdateModelMixin, GenericAPIView, ):
    """处理用户对数据操作"""
    queryset = SiteData.objects.all()
    serializer_class = RecommendSerializer
    permission_classes = [CustomIsAuthenticated]

    def post(self, request):
        """评论区操作"""
        status = str(request.data.get("status"))
        uid = request.data.get("uid")
        id = request.data.get("id")
        value = request.data.get("value")
        instance = SiteDataUser.objects.filter(sitedata__uid=uid, user=request.user).first()
        site_obj = SiteData.objects.filter(uid=uid)
        # todo 异步
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
                site_user_obj = SiteDataUser.objects.filter(user=request.user,
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
        # todo 异步
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
            self.code = 1201
            if instance:
                rating = instance.rating
                site_obj.update(rating=F('rating') - rating)
                instance.delete()
                self.code = 1000
        if not status and not instance:
            # 判断当前对象是否存在
            user_obj = UserDetail.objects.filter(id=request.user.pk, ).first()
            site_obj.update(collect_num=F('collect_num') + 1)
            # raise ValueError
            SiteDataUser.objects.create(user_id=user_obj.pk, sitedata=site_obj.first(), star=True)

        return APIResponse('', code=self.code)


class ReplyView(BaseView, ListModelMixin, CreateModelMixin, GenericAPIView):
    """评论视图类"""
    permission_classes = [CustomIsAuthenticated, ]
    serializer_class = ReplySerializer

    queryset = Comments.objects.all()

    def get_queryset(self):
        uid = self.request.query_params.get("uid").split('?')[0]
        return self.queryset.filter(reply_site_id=uid).order_by("-create_time")

    def get_permissions(self):
        if self.request.method == 'GET':
            return []
        return super(ReplyView, self).get_permissions()

    def get(self, request):
        """获取评论列表"""
        return APIResponse(self.list(request).data)

    def get_serializer(self, *args, **kwargs):
        request = self.request
        if request.method == 'GET':
            return super(ReplyView, self).get_serializer(self.get_queryset(), many=True, )
        return self.serializer_class(data=request.data, context={'request': request})

    def post(self, request):
        """用户评论"""
        return APIResponse(self.create(request).data)

    # def delete(self, request):
    #     pass


class NewsView(ListModelMixin, GenericAPIView):
    """网站日程"""
    serializer_class = NewsSerializers
    queryset = News.objects.all()

    @cache_response(timeout=datetime.timedelta(days=1).days, cache='catch')
    def get(self, request):
        return APIResponse(self.list(request).data)


class SpiderView(APIView):
    permission_classes = [CustomIsAuthenticated]

    def get(self, request):
        """爬取图片"""
        url = request.query_params.get("spider_url")
        try:
            if not url.startswith("http"):
                obj = GetSiteDetail(site_url="https://" + url)
            else:
                obj = GetSiteDetail(site_url=url)
            return APIResponse(obj.get_site_ico)
        except Exception as e:
            logger.warning(f'{url}解析错误:{e}')
            return APIResponse(-1, code=1204, msg='解析错误')


class EmailUtilView(APIView):
    """发送邮箱请求的接口"""

    #

    def post(self, request):
        email = request.data.get("email")
        pattern = Pattern()
        pattern = pattern["email"]
        if not pattern.match(email):
            return APIResponse(**{"code": 1201, "msg": "邮箱格式错误"})
        if not UserInfo.objects.filter(email=email).first():
            return APIResponse(**{"code": 1201, "msg": "邮箱不存在"})
        # 进入队列方式邮箱

        send_user_email.delay(email)
        return APIResponse(**{"code": 1000, "msg": "成功"})
