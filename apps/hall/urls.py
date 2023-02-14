from django.urls import path, re_path

from apps.hall.views import Test, RankView

urlpatterns = [
    re_path('rank', RankView.as_view()),
    re_path("test/", Test.as_view())

]
