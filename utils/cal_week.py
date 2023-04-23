# -*- coding: utf-8 -*-
# @Time : 2023/2/8 17:36
# @Site : https://www.codeminer.cn 
"""
file-name:cal_week
ex:
"""
import datetime


def get_week_key(now=None):
    if not now:
        now = datetime.datetime.now()  # 获取当前日期
    current_week = now.weekday()
    if current_week == 0:  # 0就是代表周一
        # 重写存储新的key
        date = now.date()
        return f"WEEK_RANK:{date}"
    """获取当前周上一次存储key的时间"""
    return f"WEEK_RANK:{(now.now() + datetime.timedelta(days=-current_week)).date()}"


def set_score(conn, key: str, score: int, name: str):
    """存储分数"""
    conn.zincrby(key, score, name)  # 存储周积分
    conn.zincrby('rank', score, name)  # 存储总积分


if __name__ == '__main__':
    get_week_key()
