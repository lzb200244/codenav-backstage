"""
线上配置
"""
import datetime
import os
from backstage.settings.base import *
import sys
JWT_CONF = {
    "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1)
}
# 密码加盐
EXTRACT_MD5 = "codeminer"
# media配置
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
# 极验账密
GEETEST_ID = "c853da90d7cf18e29329d0d070e800a4"
GEETTEST_KEY = "586d4ec98f95e551065892d38d4269b4"

sys.path.append(str(BASE_DIR))
sys.path.append(os.path.join(BASE_DIR, 'apps'))
# 请求跨域配置
ALLOWED_HOSTS = ["127.0.0.1", 'localhost', 'codeminer.cn']
CORS_ORIGIN_WHITELIST = [
    'http://127.0.0.1:5173',
    'https://codeminer.cn',
    'http://codeminer.cn',

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
    "DEFAULT_AUTHENTICATION_CLASSES": ["extensions.auth.baseAuth.MyBaseAuth", ],

    # 限流控制
    "DEFAULT_THROTTLE_RATES": {
        "anon": "30/m",  # 未登录
        "user": "60/m"  # 已经登录
    },
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',),
    # 线上环境配置
    # 解析器
    'DEFAULT_RENDERER_CLASSES':
        ('rest_framework.renderers.JSONRenderer',)
}

CSRF_TRUSTED_ORIGINS = ["https://www.codeminer.cn", ]
# 时区修改
LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
# 线上环境配置
DEBUG = False
"""qq密钥"""
QQ_CLIENT_ID = '102027552'
# 我们申请的 客户端秘钥
QQ_CLIENT_SECRET = 'VvCIBtOgkdJn35wZ'
# 我们申请时添加的: 登录成功后回调的路径
QQ_REDIRECT_URI = 'http://www.codeminer.cn/login'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'codenav',
        'USER': 'root',
        'PASSWORD': 'lzb200244',
        'HOST': '127.0.0.1',
        'PORT': '13308',
    }
}
APPEND_SLASH = False
REDIS_CONN = {
    "host": "127.0.0.1",
    "port": 16381,
    "password": 'lzb200244'
}

CATCH_LIST = ['default', 'account', 'operation', 'hall', 'catch', 'test']


def redis_conf(index):
    return {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://{REDIS_CONN.get('host')}:{REDIS_CONN.get('port')}/{index}",  # 安装redis的主机的 IP 和 端口
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
# todo 线上collectstatic配置
STATIC_URL = "static/"
STATIC_ROOT = "/admin"
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

# ############################################rabbitmq
RABBITMQCONF = {
    'user': 'root',
    'password': 'lzb200244',
    'port': '5673',
    'host': '127.0.0.1'
}
# 给ADMINS发送邮件需要配置
# 日志配置

LOG_ROOT = os.path.join(BASE_DIR, 'logs')
if not os.path.exists(LOG_ROOT):
    os.mkdir(LOG_ROOT)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        # 日志格式
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
        "default": {
            "format": '%(asctime)s %(name)s  %(pathname)s:%(lineno)d %(module)s:%(funcName)s '
                      '%(levelname)s- %(message)s',
            "datefmt": "%Y-%m-%d %H:%M:%S"
        },
    },
    'handlers': {
        # 名字睡意
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',  # StreamHandler处理方式
            'formatter': 'default'
        },
        # 定义一个为account的处理器
        'account': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',  # 保存日志自动切割
            'filename': os.path.join(BASE_DIR, 'logs/account.log'),
            'formatter': 'default',
            'backupCount': 4,  # 备份info.log.1 info.log.2 info.log.3 info.log.4
            'maxBytes': 1024 * 1024 * 50,  # 日志大小50m
            'encoding': 'utf-8'
        },
        "error": {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'encoding': 'utf-8',
            'filename': os.path.join(BASE_DIR, 'logs/error.log'),
            'formatter': 'default',
            'backupCount': 5,  # 备份info.log.1 info.log.2 info.log.3 info.log.4
            'maxBytes': 1024 * 1024 * 50,  # 日志大小50m
        },
        # 服务错误
        "server": {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/server.log'),
            'formatter': 'default'
        },
        # 请求
        "request": {
            'level': 'DEBUG',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/request.log'),
            'when': 'D',
            'backupCount': 4,
            'encoding': 'utf-8',
            'formatter': 'default'
        },

        "waring": {
            'level': 'WARNING',
            'class': 'logging.handlers.TimedRotatingFileHandler',  # 按时间分类存储日志文件
            'filename': os.path.join(BASE_DIR, 'logs/waring.log'),
            'when': 'D',
            'backupCount': 4,
            'encoding': 'utf-8',
            'formatter': 'default'
        },
        "operation": {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'encoding': 'utf-8',
            'filename': os.path.join(BASE_DIR, 'logs/operation.log'),
            'formatter': 'default',
            'backupCount': 3,  # 备份info.log.1 info.log.2 info.log.3 info.log.4
            'maxBytes': 1024 * 1024 * 50,  # 日志大小50m
        },

    },
    # 日志实例对象
    # 所有的实例对象凡是有日志记录这里都会有一份
    'loggers': {
        '': {
            'handlers': ['waring', 'console', 'error'],
            'level': 'DEBUG',
            'propagate': True  # 是否向上传递日志
        },
        # 推荐时的日志
        'operation': {
            'handlers': ['operation'],
            'level': 'INFO'
        },
        'account': {
            'handlers': ['account'],
            'level': 'INFO'
        },
        # 后台错误时500
        "django.request": {
            "level": "DEBUG",
            "handlers": ["request"],
            'propagate': False,
        },
        # 每次请求时
        "django.server": {
            "level": "DEBUG",
            "handlers": ["server"],
            'propagate': False,
        },

    }

}
