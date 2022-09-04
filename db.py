import redis


# 连接redis
def connect_redis():
    pool = redis.ConnectionPool(host="127.0.0.1", port=6379, db=0)
    r = redis.Redis(connection_pool=pool)
    return r
