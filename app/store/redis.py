from redis import Redis, ConnectionPool
from app.config import load_config


def create_redis_pool():
    config = load_config()
    return ConnectionPool(
        host=config.redis.host,
        port=int(config.redis.port),
        db=config.redis.db,
        password=config.redis.password,
        decode_responses=True,
        encoding="utf-8"
    )


pool = create_redis_pool()


def get_redis_client():
    return Redis(connection_pool=pool)
