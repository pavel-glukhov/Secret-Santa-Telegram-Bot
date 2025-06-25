from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.config import load_config

JOB_STORES = {
    'default': RedisJobStore(
        host=load_config().redis.host,
        port=load_config().redis.port,
        password=load_config().redis.password
    ),
}

scheduler = AsyncIOScheduler(
    jobstores=JOB_STORES,
)
