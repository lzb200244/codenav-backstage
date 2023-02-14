import django_filters

from apps.account.models import UserInfo


class UserFilter(django_filters.FilterSet):
    class Meta:
        model = UserInfo
        fields = ["username", "token", "detail"]
