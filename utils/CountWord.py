import json

from django_redis import get_redis_connection

"""统词器"""
REDIS_POOL = get_redis_connection('account')


class CountWord(object):
    """记录词出现的次数生成词语图"""

    def __init__(self, value):
        if not REDIS_POOL.exists("wordCloud"):
            REDIS_POOL.set("wordCloud", json.dumps({}, ensure_ascii=False), ex=60 * 60 * 24 * 7)
        self.wordCloud = json.loads(REDIS_POOL.get("wordCloud"))
        self.exist_value(value)

    def exist_value(self, value):
        count = self.wordCloud.get(value)
        if count:
            """如果存在这个值+1"""
            self.wordCloud.update({value: count + 1})
            return self
        else:
            self.wordCloud[value] = 1
            return self

    def set(self):
        REDIS_POOL.set("wordCloud", json.dumps(self.wordCloud, ensure_ascii=False))
        return self

    @staticmethod
    def get():
        return json.loads(REDIS_POOL.get("wordCloud"))
