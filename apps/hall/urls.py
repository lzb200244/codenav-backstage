from django.urls import path

from apps.hall.views import (RankView, ChatSView, CircleView,
                             StimulateGoodsView, CustomRecordView)

urlpatterns = [
    # 排名
    path('rank', RankView.as_view()),
    # path("test", Test.as_view()),
    path("chat", ChatSView.as_view()),
    path("circle", CircleView.as_view()),
    path("stimulate", StimulateGoodsView.as_view()),
    path("order", CustomRecordView.as_view()),

]
