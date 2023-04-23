from django.conf import settings
from django.contrib import admin
from django.urls import path, re_path, include
from django.views.static import serve

urlpatterns = [
    # 管理员
    path('codeminer-admin/', admin.site.urls),
    re_path(r'media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    path('api/', include(
        [
            re_path('account/', include('apps.account.urls')),
            re_path('operation/', include('apps.operation.urls')),
            re_path('hall/', include("apps.hall.urls"))
        ],
    )),

]
