"""腾讯cos"""
from qcloud_cos import CosConfig, CosS3Client

from django.conf import settings


class TencentCos():
    def __init__(self): pass

    def upload_file(self, local_file_name, file_name, region="ap-nanjing", bucket="siteimages-1311013567"):
        """
        腾讯cos文件存储对象
        :param bucket: 桶名称
        :param local_file_name: 文件名
        :param file_name: 文件
        :param region: 地区
        """
        # 根据文件大小自动选择简单上传或分块上传，分块上传具备断点续传功能。
        config = CosConfig(Region=region, SecretId=settings.
                           TENCENT_SECRET_ID, SecretKey=settings.TENCENT_SECRET_KEY)
        client = CosS3Client(config)
        response = client.upload_file_from_buffer(
            Bucket=bucket,  # 上传到桶的名称
            Body=local_file_name,  # 文件对象 file对象
            Key=file_name,  # 上传到桶之后的文件名
        )
        return f"https://{bucket}.cos.{region}.myqcloud.com/{file_name}"

    def delete_file(self, file_name, region="ap-nanjing", bucket="userimages-1311013567"):
        """# 单个cos删除文件"""
        # 根据文件大小自动选择简单上传或分块上传，分块上传具备断点续传功能。
        config = CosConfig(Region=region, SecretId=TENCENT_SECRET_ID, SecretKey=settings.TENCENT_SECRET_KEY)
        client = CosS3Client(config)
        response = client.delete_object(
            Bucket=bucket,  # 上传到桶的名称
            Key=file_name,  # 上传到桶之后的文件名
        )
        return f"https://{bucket}.cos.{region}.myqcloud.com/{file_name}"

    pass


tencent = TencentCos()

if __name__ == '__main__':
    pass
