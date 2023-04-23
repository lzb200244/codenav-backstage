# 主程序
import os
from celery import Celery

# 加载离线脚本
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backstage.settings.prod")

# 创建celery实例对象
app = Celery("sms")

# 通过app对象加载配置
app.config_from_object("mycelery.mytasks.config")
# celery -A mytasks worker --loglevel=info
# 加载任务
# 参数必须必须是一个列表，里面的每一个任务都是任务的路径名称
# app.autodiscover_tasks(["任务1","任务2"])
app.autodiscover_tasks(["mycelery.mytasks.email"], )

# 启动Celery的命令
# 强烈建议切换目录到mycelery根目录下启动
# celery -A mycelery.main worker --loglevel=info
