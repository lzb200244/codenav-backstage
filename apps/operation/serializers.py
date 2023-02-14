from django.db.models import F, Sum
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from apps.account.models import SiteData, SiteDataUser, UserDetail
from apps.operation.models import Comments, Inform, News
from utils.GetSiteDetail import GetSiteDetail
from utils.Tencent.text_check import TextCheck
from utils.md5 import make_uuid
from utils.response_status import APIResponse


class RecommendSerializer(serializers.ModelSerializer):
    datatype = serializers.SerializerMethodField(read_only=True)
    uid = serializers.SerializerMethodField(read_only=True)
    sitedatauser = serializers.SerializerMethodField(read_only=True)
    rating = serializers.SerializerMethodField(read_only=True)

    def get_uid(self, val):
        return val.uid

    def get_sitedatauser(self, val):

        use_obj = SiteDataUser.objects.filter(
            sitedata=val,

            user=self.context['request'].user_obj).first()
        if use_obj:
            return {
                "star": use_obj.star
            }
        return {
            "star": False
        }

    def get_rating(self, val):

        uid = self.context['request'].data.get("uid")
        site_data_user_obj = SiteDataUser.objects.filter(sitedata=val)
        if uid:
            site_data_user_obj = SiteDataUser.objects.filter(sitedata__uid=uid)
        count = site_data_user_obj.count()
        total = site_data_user_obj.aggregate(total=Sum("rating"))
        rating = total.get("total") if not count else total.get("total") / count
        dic = {
            "rating": rating,
            "rated": False
        }
        # 如果用户没有登录就返回
        user = self.context['request'].user_obj
        if not user:
            return dic
        # 登入用户已评分
        site_user_obj = SiteDataUser.objects.filter(user=user,
                                                    sitedata__uid=uid).first()
        if site_user_obj and site_user_obj.rated:
            dic["rated"] = True
        return dic

    def get_datatype(self, val):
        return [item.categories for item in val.datatype.all()]

    def get_update_time(self, val):
        return val.update_time.strftime("%Y-%m-%d %H:%M")

    class Meta:
        model = SiteData
        fields = [
            "site_url", "name", "img_url",
            "introduce", "datatype",
            "sitedatauser", "uid", "collect_num", "rating"
        ]

    def create(self, validated_data):
        user = self.context['request'].user
        datatype = self.context['request'].data.get("datatype")
        url = validated_data.get("site_url")
        isvalid = 1
        if not url.startswith("http"):
            site_url = "http://" + url
        else:
            site_url = url
        if GetSiteDetail(site_url).get_status != 1:
            isvalid = 2
        name = validated_data.get("name")
        img_url = validated_data.get("img_url")
        introduce = validated_data.get("introduce")
        instance = SiteData.objects.create(
            site_url=site_url, name=name, img_url=img_url, introduce=introduce,
            recommend=user, isvalid=isvalid, uid=make_uuid().hex
        )
        UserDetail.objects.filter(userinfo=user).update(score=F('score') + 1)  # 用户推荐加分
        if isinstance(datatype, list):
            instance.datatype.add(*datatype)
        return instance


class ReplySerializer(serializers.ModelSerializer):
    """评论"""
    createTime = serializers.SerializerMethodField(read_only=True)
    username = serializers.SerializerMethodField(read_only=True)
    avatar = serializers.SerializerMethodField(read_only=True, required=False)
    reply = serializers.SerializerMethodField(read_only=True, required=False)

    def get_createTime(self, val):
        return val.create_datetime.strftime("%Y-%m-%d %H:%M")

    def get_creator(self, val):
        pass

    def get_username(self, val):
        return val.creator.detail.name

    def get_avatar(self, val):
        return val.creator.detail.userAvatar

    def get_reply(self, val):
        import random
        lst = []

        for item in Comments.objects.filter(parentId=val.id).all():
            lst.append({
                "id": item.id,
                "avatar": item.creator.detail.userAvatar,
                "parentId": item.parentId.id,
                "username": item.creator.detail.name,
                "level": 1,
                "content": item.content,
                "address": random.choice(["IP:火星", "IP:木星", "IP:猫星球", "IP:天文星"]),
                "like": item.like,
                "createTime": item.create_datetime.strftime("%Y-%m-%d %H:%M"),
                "reply": []
            })
        return {
            "total": len(lst), "list": lst
        }

    creator = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Comments
        exclude = ["reply_site"]

    def create(self, validated_data, ):
        request = self.context['request']
        user_obj = request.user
        content = request.data.get("content")
        reply_site = request.data.get("reply_site")
        parentId = request.data.get("parentId")
        check = TextCheck()
        """文本监测"""
        label = check.check(content=content).get('label')
        if check.check(content=content).get('label') is not True:
            # 添加消息
            Inform.objects.create(
                user=user_obj,
                content=f'尊敬的用户,请注意你在该 <a style="color:red;font-weight: bolder"  href="/detail/{reply_site}"> 点击跳转 '
                        f'</a>的评论语言,良言一句三冬暖，恶语伤人六月寒!',
                type=4
            )
            raise ValidationError(detail=APIResponse(data='', msg=label, code=1202).data)
        if parentId:
            """用户回复"""
            user = Comments.objects.get(pk=parentId).creator
            if user is not user_obj:  # 不回复自己
                Inform.objects.create(
                    user=user,
                    content=f"""有人回复了你的评论<a style="color:red;font-weight: bolder"  href="/detail/{reply_site}"> 点击跳转 
                    </a>""",
                    type=3
                )
        instance = Comments.objects.create(
            creator=user_obj,
            content=content,
            reply_site_id=reply_site,
            parentId_id=parentId
        )
        instance.save()
        return instance


class SiteDetailSerializers(serializers.ModelSerializer):
    datatype = serializers.SerializerMethodField(read_only=True)
    recommend = serializers.SerializerMethodField(read_only=True)
    sitedatauser = serializers.SerializerMethodField(read_only=True)
    update_time = serializers.SerializerMethodField(read_only=True)
    rating = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = SiteData
        fields = [
            "site_url", "name", "img_url",
            "introduce", "datatype",
            "sitedatauser", "uid", "collect_num", "rating", 'update_time', 'recommend'
        ]

    def get_update_time(self, val):

        return val.update_time.strftime("%Y-%m-%d %H:%M")

    def get_datatype(self, val):
        return [item.categories for item in val.datatype.all()]

    def get_recommend(self, val):
        return {
            "name": val.recommend.detail.name,
            "recommend_avatar": val.recommend.detail.userAvatar
        }

    def get_sitedatauser(self, val):
        # user = self.context['request'].user_obj
        # if user:
        #     print(SiteDataUser.objects.filter(sitedata=val))
        #     user_obj = SiteDataUser.objects.filter(sitedata=val)
        #     print(user_obj)
        #     return {
        #         "star": user_obj.star
        #     }
        return {
            "star": False
        }

    def get_rating(self, val):
        user = self.context['request'].user_obj
        uid = self.context['request'].data.get("uid")
        site_data_user_obj = SiteDataUser.objects.filter(sitedata=val)
        if uid:
            site_data_user_obj = SiteDataUser.objects.filter(sitedata__uid=uid)
        count = site_data_user_obj.count()
        total = site_data_user_obj.aggregate(total=Sum("rating"))
        rating = total.get("total") if not count else total.get("total") / count
        dic = {
            "rating": 4,
            "rated": False
        }
        # 如果用户没有登录就返回
        if not user:
            return dic
        # 登入用户已评分
        site_user_obj = SiteDataUser.objects.filter(user=user,
                                                    sitedata__uid=uid).first()

        if site_user_obj and site_user_obj.rated:
            dic["rated"] = True
        return dic


class NewsSerializers(serializers.ModelSerializer):
    type = serializers.CharField(max_length=16, read_only=True, source='get_type_display')
    color = serializers.CharField(max_length=16, read_only=True, source='get_color_display')

    class Meta:
        model = News

        ordering = ['create_time']
        fields = '__all__'
