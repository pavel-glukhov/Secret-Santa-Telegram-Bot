from redis import Redis
from app.config import load_config


def get_redis_client():
    config = load_config()
    return Redis(host=config.redis.host,
                 port=int(config.redis.port),
                 db=config.redis.db,
                 password=config.redis.password,
                 decode_responses=True,
                 encoding="utf-8")
