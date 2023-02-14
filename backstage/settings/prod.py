"""
线上配置
"""
import os
from backstage.settings.base import *

# 密码加盐
EXTRACT_MD5 = "codeminer"
# media配置
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
# 极验账密
GEETEST_ID = "c853da90d7cf18e29329d0d070e800a4"
GEETTEST_KEY = "586d4ec98f95e551065892d38d4269b4"
import sys

sys.path.append(str(BASE_DIR))
sys.path.append(os.path.join(BASE_DIR, 'apps'))
# 请求跨域配置
CORS_ALLOW_CREDENTIALS = True  # 允许所有的请求头
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_HEADERS = ('*',)

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
    "DEFAULT_AUTHENTICATION_CLASSES": ["utils.auth.baseAuth.MyBaseAuth", ],
    # 限流控制
    "DEFAULT_THROTTLE_RATES": {
        "anon": "30/m",  # 未登录
        "user": "60/m"  # 已经登录
    },
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',),
    # 线上环境配置
    # 解析器
    #    'DEFAULT_RENDERER_CLASSES':
    #        ('rest_framework.renderers.JSONRenderer',)
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
        'PASSWORD': '200244',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
}
REDIS_CONN = {
    "host": "172.17.0.3",
    "port": 6379,
    "password": 200244
}
APPEND_SLASH = False
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://{REDIS_CONN.get('host')}:6379",  # 安装redis的主机的 IP 和 端口
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "CONNECTION_POOL_KWARGS": {
                "max_connections": 1000,
                "encoding": 'utf-8'
            },
            "PASSWORD": REDIS_CONN.get('password')  # redis密码
        }
    },
    "account": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://{REDIS_CONN.get('host')}:6379/2",  # 安装redis的主机的 IP 和 端口
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "CONNECTION_POOL_KWARGS": {
                "max_connections": 1000,
                "encoding": 'utf-8'
            },
            "PASSWORD": REDIS_CONN.get('password')
        }
    },

}
# todo 线上collectstatic配置
# STATIC_URL = "admin/static"
# STATIC_ROOT = STATIC_URL
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
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',  # StreamHandler处理方式
            'formatter': 'default'
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.TimedRotatingFileHandler',  # 按时间分类存储日志文件
            'filename': os.path.join(BASE_DIR, 'logs/debug.log'),
            'when': "D",
            'interval': 1,
            'formatter': 'default'
        },
        "request": {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/request.log'),
            'formatter': 'default'
        },
        # 请求
        "server": {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/server.log'),
            'formatter': 'default'
        },
        "root": {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/root.log'),
            'formatter': 'default'
        },

        "db_backends": {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/db_backends.log'),
            'formatter': 'default'
        },
        # 好像是改变了文件内容就会记录
        "autoreload": {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/autoreload.log'),
            'formatter': 'default'
        }
    },
    'loggers': {
        # 应用中自定义日志记录器
        'custom_logs': {
            'level': 'DEBUG',
            'handlers': ['console', 'file'],
            'propagate': True,
        },
        "django": {
            "level": "DEBUG",
            "handlers": ["console", "file"],
            'propagate': False,
        },
        # 请求处理相关的日志消息。5xx响应被提升为错误消息；4xx响应被提升为警告消息。
        "django.request": {
            "level": "DEBUG",
            "handlers": ["request"],
            'propagate': False,
        },
        "django.server": {
            "level": "DEBUG",
            "handlers": ["server"],
            'propagate': False,
        },
        # 代码与数据库交互的消息
        "django.db.backends": {
            "level": "DEBUG",
            "handlers": ["db_backends"],
            'propagate': False,
        },
        "django.utils.autoreload": {
            "level": "INFO",
            "handlers": ["autoreload"],
            'propagate': False,
        }
    },
    'root': {
        "level": "DEBUG",
        "handlers": ["root"],
    }
}
