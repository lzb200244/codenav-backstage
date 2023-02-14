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


#
# pip install -r requirements.txt -i http://pypi.douban.com/simple --trusted-host pypi.douban.com
import base64

str = 'admin'
str = str.encode('utf-8')
# 加密
bs64 = base64.b64encode(str)

bs32 = base64.b32encode(str)
print(bs32)
# 结果是  b'MFSG22LO'

bs16 = base64.b16encode(str)
print(bs16)
# 结果是  b'61646D696E'

# 解密
