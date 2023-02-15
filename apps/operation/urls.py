from django.urls import re_path

from apps.operation.views import (save_file, SiteDataOperation, ReplyView,
                                  SiteListView, EmailUtilView, SiteDetailView, AllSelects, NewsView, SpiderView)

urlpatterns = [
    # 推荐
    re_path(r"opt", SiteDataOperation.as_view()),
    # 评论
    re_path(r"reply", ReplyView.as_view()),
    # 上传图片
    re_path("uploadfile", save_file),
    # 爬取图片
    re_path("spider", SpiderView.as_view()),
    # 外部接口
    # re_path("outerApi", OuterApi.as_view()),
    # 发送邮箱
    re_path("email", EmailUtilView.as_view()),
    re_path(r"sitedatas", SiteListView.as_view()),
    # 单页面数据
    re_path(r"detail", SiteDetailView.as_view()),
    # 所有选项
    re_path(r"all_select", AllSelects.as_view()),
    # 项目日程
    re_path(r"news", NewsView.as_view()),
]
