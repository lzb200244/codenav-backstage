from django.urls import path, re_path

from apps.account.views import AccountView, Tencent, RecommendListView, InformView
from rest_framework import routers

router = routers.SimpleRouter()


urlpatterns = [
    # 校验
    # re_path("codevalid", AccountCode.as_view()),
    # 用户
    path("user", AccountView.as_view()),
    path("tencent", Tencent.as_view()),
    path('recommend', RecommendListView.as_view()),
    path('informs', InformView.as_view()),

]
