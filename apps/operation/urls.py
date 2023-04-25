from django.urls import path

from apps.operation.views import (BillBoardView, SiteDataOperation, ReplyView,
                                  SiteListView, EmailUtilView, SiteDetailView, AllSelects, NewsView, SpiderView,
                                  ImageUpdateView, SimilarRecommendation)

urlpatterns = [
    # 点赞与收藏
    path(r"opt", SiteDataOperation.as_view(), name='opt'),
    # 静态数据加载
    path(r"board", BillBoardView.as_view(), name='board'),
    # 评论
    path(r"comment", ReplyView.as_view(), name='comment'),
    # 上传图片
    path("uploadfile", ImageUpdateView.as_view(), name='uploadfile'),
    # 爬取图片
    path("spider", SpiderView.as_view(), name='spider'),
    # 外部接口
    # re_path("outerApi", OuterApi.as_view()),
    # 发送邮箱
    path("email", EmailUtilView.as_view(), name='email'),
    # 所有数据
    path(r"pages", SiteListView.as_view(), name='pages'),
    # 单页面数据
    path(r"detail", SiteDetailView.as_view(), name='detail'),
    # 所有选项
    path(r"all_select", AllSelects.as_view(), name='all_select'),
    # 项目日程
    path(r"news", NewsView.as_view(), name='news'),
    path(r"recommend", SimilarRecommendation.as_view(), name='news'),

]
