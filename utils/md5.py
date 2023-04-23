import hashlib
import uuid
from django.conf import settings


def md5(val):
    # 实例化对象
    obj = hashlib.md5(settings.EXTRACT_MD5.encode("utf-8"))
    # 写入要加密的字节
    obj.update(('' + val).encode("utf-8"))
    # 获去密文
    return obj.hexdigest()


def make_uuid():
    """生成token"""
    return uuid.uuid4()






