from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.config import app_config

JOB_STORES = {
    'default': RedisJobStore(
        host=app_config().redis.host,
        port=app_config().redis.port,
        password=app_config().redis.password
    ),
}

scheduler = AsyncIOScheduler(
    jobstores=JOB_STORES,
)
