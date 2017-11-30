import redis
from datetime import datetime


class RedisCache(object):
    """ Redis操作函数 """

    def connect(self, host, port, db):
        pool = redis.ConnectionPool(host=host,
                                    port=port,
                                    db=db)
        self.r = redis.Redis(connection_pool=pool)

    def set(self, key, value, expired=None):
        if isinstance(value, str):
            if expired and isinstance(expired, datetime):
                dif = expired - datetime.now()
                seconds = int(dif.total_seconds())
                if seconds < 0:
                    seconds = 0
                expired = seconds
            else:
                expired = None

            self.r.set(key, value, ex=expired)

    def get(self, key):
        return self.r.get(key)
