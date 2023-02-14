from rest_framework.authentication import BaseAuthentication, TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
from apps.account.models import UserInfo
from utils.redis_pool import REDIS_POOL
from utils.response_status import APIResponse


class LoginAuth(BaseAuthentication):
    response = None

    def authenticate(self, request):
        token = request.META.get("HTTP_TOKEN")
        if not token:
            self.response = APIResponse(msg="请先登入", )
            raise AuthenticationFailed(detail=self.response)
        if not REDIS_POOL.exists(token):
            self.response = APIResponse(msg="token过期", )
            raise AuthenticationFailed(detail=self.response)
        user_id = REDIS_POOL.get(token)
        user_obj = UserInfo.objects.filter(id=user_id).first()
        return user_obj, token
