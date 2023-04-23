# -*- coding: utf-8 -*-
# @Time : 2023/2/7 17:30
# @Site : https://www.codeminer.cn 
"""
file-name:text_check
ex:腾讯云文本安全监测
"""
import base64
import json
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.tms.v20201229 import tms_client, models
from django.conf import settings


class TextCheck:
    def check(self, content):
        try:
            cred = credential.Credential(settings.TENCENT_SECRET_ID, settings.TENCENT_SECRET_KEY)
            httpProfile = HttpProfile()
            httpProfile.endpoint = "tms.tencentcloudapi.com"
            clientProfile = ClientProfile()
            clientProfile.httpProfile = httpProfile

            client = tms_client.TmsClient(cred, "ap-beijing", clientProfile)
            req = models.TextModerationRequest()
            params = {
                "Content": str(base64.b64encode(content.encode('utf-8')), "utf-8")
            }
            req.from_json_string(json.dumps(params))
            resp = client.TextModeration(req)
            # 输出json格式的字符串回包

            res = json.loads(resp.to_json_string())
            check_rule = {
                'Normal': True,
                "Porn": ['评论存在色情等关键字,注意言论'],
                "Abuse": '评论存在谩骂等关键字,注意言论',
                "Ad": '广告评论,推广告要钱!!!',
            }
            return {
                "label": check_rule.get(res['Label'])
            }

        except TencentCloudSDKException as err:
            return {
                'label': True,
            }
            pass
        except Exception as e:
            print(e)
            # print(err)


if __name__ == '__main__':
    check = TextCheck()
