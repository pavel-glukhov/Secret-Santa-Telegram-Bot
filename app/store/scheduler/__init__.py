from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.config import config

JOB_STORES = {
    'default': RedisJobStore(
        host=config.redis.host,
        port=config.redis.port,
        password=config.redis.password
    ),
}

scheduler = AsyncIOScheduler(
    jobstores=JOB_STORES,
)
