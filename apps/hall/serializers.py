# -*- coding: utf-8 -*-
# @Time : 2023/2/5 22:16
# @Site : https://www.codeminer.cn 
"""
file-name:serializers
ex:
"""
from rest_framework import serializers

from apps.account.models import UserInfo
from apps.hall.models import ChatModel, StimulateModel, CustomRecord


class RankSerializers(serializers.ModelSerializer):
    score = serializers.CharField(read_only=True, source='detail.score')
    avatar = serializers.CharField(read_only=True, source='detail.userAvatar')
    user = serializers.SerializerMethodField()

    class Meta:
        model = UserInfo
        fields = ['username', 'avatar', 'score', 'user']

    def get_user(self, query):
        user_obj = query.creator
        return user_obj.make_user_info()


class ChatSerializers(serializers.ModelSerializer):
    create_time = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()

    def get_create_time(self, query):
        return query.create_time.strftime("%Y-%m-%d %H:%M")

    def get_user(self, query):
        user_obj = query.creator
        return user_obj.make_user_info(self.context['request'].user)

    class Meta:
        model = ChatModel
        fields = '__all__'

        extra_kwargs = {
            item: {'read_only': True} for item in ["content", "create_time", "title", 'creator']
        }

    # 无限点赞
    def update(self, instance, validated_data):
        instance.like += 1
        instance.save()
        return instance


class StimulateGoodsSerializers(serializers.ModelSerializer):
    class Meta:
        model = StimulateModel
        fields = '__all__'


class CustomRecordSerializers(serializers.ModelSerializer):
    status = serializers.CharField(source='get_status_display')
    goods = serializers.SerializerMethodField()
    customer = serializers.CharField(source='customer.detail.name')

    class Meta:
        model = CustomRecord
        fields = '__all__'

    def get_goods(self, query):
        return {
            'title': query.goods.title,
            'price': query.goods.price,
            'type': query.goods.get_type_display(),
            'img': query.goods.img,

        }
