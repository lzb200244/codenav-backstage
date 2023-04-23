from django.urls import path

from rest_framework.views import APIView

from apps.account.views import AccountView, Tencent, RecommendListView, InformView, RegisterView
from rest_framework import routers

from utils.response import APIResponse

router = routers.SimpleRouter()


class Test(APIView):

    # permission_classes = [CustomIsAuthenticated]

    def get(self, request):
        print(request.user)
        return APIResponse("ok")


urlpatterns = [
    # 校验

    # 用户
    path('test', Test.as_view()),
    path("user", AccountView.as_view()),
    path("register", RegisterView.as_view()),
    # qq登录
    path("tencent", Tencent.as_view()),
    # 用户推荐
    path('recommend', RecommendListView.as_view()),
    # 网站日程
    path('informs', InformView.as_view()),

]
