# -*- coding: utf-8 -*-
# @Time : 2023/2/5 22:16
# @Site : https://www.codeminer.cn 
"""
file-name:serializers
ex:
"""
from rest_framework import serializers

from apps.account.models import UserInfo


class RankSerializers(serializers.ModelSerializer):
    score = serializers.CharField(read_only=True, source='detail.score')
    avatar = serializers.CharField(read_only=True, source='detail.userAvatar')

    class Meta:
        model = UserInfo
        fields = ['username', 'avatar', 'score']
