import random
from django.core.mail import send_mail

from django.conf import settings
from django_redis import get_redis_connection

conn = get_redis_connection('account')


class SendEmail(object):
    def make_int(self):
        """整数类型验证码"""
        return random.randrange(10000, 99999)

    def make_str(self):
        """字符串类型验证码"""
        import string
        return ''.join(random.sample(string.hexdigits, 6))

    def config(self, title, to, msg, code='str', froms=settings.EMAIL_HOST_USER):
        """
        :param title: 主题
        :param to:  邮件接收者列表
        :param msg: 内容
        :param code: 发件类型
        :param froms: 发件人
        :return:
        """
        subject = title  # 主题
        from_email = froms  # 发件人，在settings.py中已经配置
        to_email = to  # 邮件接收者列表
        code = getattr(self, f'make_{code}')
        code = code()
        message = msg if msg else f'验证码为:{code}'  # 正文
        # meg_html = '<a href="http://www.baidu.com">点击跳转</a>'  # 发送的是一个html消息 需要指定
        try:

            send_status = send_mail(subject, message, from_email, [to_email, ], )

        except:
            # 邮箱格式错误
            return False
        print(222)
        print(to_email)
        print('杀杀杀')
        conn.set(to_email, code, ex=60 * 2)
        print(conn.get(to_email))

        return True if send_status == 1 else False


SENDEMAIL = SendEmail()

if __name__ == '__main__':
    # print("邮箱")
    pass
