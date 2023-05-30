import redis.asyncio as async_redis

from config import REDIS_HOST, REDIS_PORT, REDIS_DB


class RedisConnection:
    def __init__(self):
        self.pool = async_redis.ConnectionPool(host=REDIS_HOST,
                                               port=REDIS_PORT,
                                               db=REDIS_DB)

    def get_client(self):
        return async_redis.StrictRedis(connection_pool=self.pool,
                                       decode_responses=True)
