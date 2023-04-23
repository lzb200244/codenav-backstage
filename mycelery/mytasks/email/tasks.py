# celery的任务必须写在tasks.py的文件中，别的文件名称不识别!!!
from django.conf import settings
from django.db.models import Count

from apps.account.models import SiteData, UserInfo
from apps.operation.models import Inform
from mycelery.mytasks.main import app
import logging

from utils.Tencent.sendemial import SENDEMAIL

log = logging.getLogger("django")


@app.task
def send_email_to_admin():
    """发送短信"""

    check_count = SiteData.objects.filter(isvalid=1).aggregate(check_count=Count("uid"))
    """放入任务队列发送邮箱给管理员"""
    SENDEMAIL.config("CodeMiner-site", to=settings.ADMIN_EMAIL,
                     msg="有用户推荐新资源,当前待审核资源为:%s,你可以点击前往过审%s" % (
                         check_count.get("check_count"),
                         "http://43.138.105.186:8888/codeminer-admin/#/codeminer-admin/account/sitedata/"
                     ))

    return 'ok'


@app.task
def send_user_email(email):
    res = SENDEMAIL.config(title="CodeMiner-site", msg="", to=email,
                           code='str')
    if not res:
        # 发送邮箱失败
        # 此时的邮箱一定存在
        user_obj = UserInfo.objects.get(email=email)
        # 创建通知记录
        Inform.objects.create(
            type=5, user=user_obj,
            content=f'尊敬的{user_obj.username}，你的邮箱存在错误。错误邮箱号码为：{email}，请你到站内进行修改，https://codeminer.cn'
        )
