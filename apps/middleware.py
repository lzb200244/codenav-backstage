from django.utils.deprecation import MiddlewareMixin
from apps.account.models import UserInfo

from utils.response_status import APIResponse


class CoreMiddleWare(MiddlewareMixin):

    def process_request(self, request):
        meta = request.META

        user_pk = UserInfo.objects.filter(token=meta.get("HTTP_TOKEN"))
        request.user_obj = None
        if user_pk.exists():
            request.user_obj = user_pk.first()

    def process_exception(self, request, exception):
        """
        统一异常处理
        :param request: 请求对象
        :param exception: 异常对象
        :return:
        """
        # 异常处理

        return APIResponse("", msg="Illegal requests were also denied", code=1500, status=404)
