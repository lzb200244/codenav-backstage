import redis



"""redis连接池"""

from django.conf import settings

pool = redis.ConnectionPool(host=settings.REDIS_CONN.get("host", "127.0.0.1"),
                            port=settings.REDIS_CONN.get("port", "6379"),
                            decode_responses=True, max_connections=10, )
REDIS_POOL = redis.Redis(connection_pool=pool, password=settings.REDIS_CONN.get("password", "root"),)
