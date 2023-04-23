"""本地配置"""
import datetime

from backstage.settings.base import *
from django.conf import settings
import sys
import os

sys.path.append(str(BASE_DIR))
sys.path.append(os.path.join(BASE_DIR, 'apps'))
# 密码加盐
EXTRACT_MD5 = "codeminer"
# media配置
MEDIA_ROOT = os.path.join(settings.BASE_DIR, 'media')

# 请求跨域配置
ALLOWED_HOSTS = ["127.0.0.1", 'localhost']
CORS_ORIGIN_WHITELIST = [
    'http://127.0.0.1:5173',
    'http://localhost:5173',

]
# 允许发送 cookies
CORS_ALLOW_CREDENTIALS = True
# 允许所有请求方法
CORS_ALLOW_ALL_ORIGINS = True
# 允许所有头信息
CORS_ALLOW_HEADERS = '*'

# 腾讯信息
TENCENT_SECRET_ID = 'AKID1vRjtra5MTT8d4R7YkhS0KTSDj04DBuR'  # 替换为用户的 SecretId，请登录访问管理控制台进行查看和管理，https://console.cloud.tencent.com/cam/capi
TENCENT_SECRET_KEY = 'QdcNtCI9mBLGOHyRffR1OhmfMq55rSq1'  # 替换为用户的 SecretKey，请登录访问管理控制台进行查看和管理，https://console.cloud.tencent.com/cam/capi
REGION = 'ap-nanjing'

# QQ邮箱发送配置
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.qq.com'  # 腾讯QQ邮箱 SMTP 服务器地址
EMAIL_PORT = 25  # SMTP服务的端口号
EMAIL_HOST_USER = '1405839758@qq.com'  # 你的qq邮箱，邮件发送者的邮箱
EMAIL_HOST_PASSWORD = 'mjghadywnsiehaab'  # 你申请的授权码
EMAIL_USE_TLS = False  # 与SMTP服务器通信时,是否启用安全模式
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER  # 默认发件用户

# rest_framework配置
REST_FRAMEWORK = {
    # JWTAuthentication2
    "DEFAULT_AUTHENTICATION_CLASSES": ["extensions.auth.baseAuth.MyBaseAuth",
                                       "extensions.auth.jwtauthentication.JWTAuthentication2"],

    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',),
    # 线上环境配置
    # 解析器

}

CSRF_TRUSTED_ORIGINS = ["https://www.codeminer.cn", ]
# 时区修改
LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
# 线上环境配置
DEBUG = True
JWT_CONF = {
    "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1)
}
"""qq密钥"""
QQ_CLIENT_ID = '102027552'
# 我们申请的 客户端秘钥
QQ_CLIENT_SECRET = 'VvCIBtOgkdJn35wZ'
# 我们申请时添加的: 登录成功后回调的路径
QQ_REDIRECT_URI = 'http://www.codeminer.cn/login'

REDIS_CONN = {
    "host": "localhost",
    "port": 6379,
    "password": 'root'
}
APPEND_SLASH = False
CATCH_LIST = ['default', 'account', 'operation', 'hall', 'catch', 'test']


def redis_conf(index):
    return {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://{REDIS_CONN.get('host')}:6379/{index}",  # 安装redis的主机的 IP 和 端口
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "CONNECTION_POOL_KWARGS": {
                "max_connections": 1000,
                "encoding": 'utf-8'
            },
            "PASSWORD": REDIS_CONN.get('password')  # redis密码
        }
    }


CACHES = {
    item: redis_conf(index) for index, item in enumerate(CATCH_LIST)
}

ADMIN_EMAIL = "2632141215@qq.com"

""" simpleUi配置 """
# 后台log

SIMPLEUI_LOGO = 'https://codeminer.cn/siteico.png'
# 首页标题
SIMPLEUI_HOME_TITLE = '不懂就搜索'
# 首页默认线上
SIMPLEUI_HOME_PAGE = 'https://cn.bing.com/?mkt=zh-CN'
# SIMPLEUI_HOME_ICON = 'fa fa-user'
# 首页跳转地方
SIMPLEUI_INDEX = 'https://codeminer.cn/'
SIMPLEUI_HOME_INFO = True
# 快速操作
SIMPLEUI_HOME_QUICK = True
# 最近动作
SIMPLEUI_HOME_ACTION = True

"""
日志
"""
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
