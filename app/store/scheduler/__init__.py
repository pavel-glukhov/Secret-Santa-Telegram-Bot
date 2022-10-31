from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.config import config

job_stores = {
    'default': RedisJobStore(
        host=config.redis.host,
        port=config.redis.port,
        password=config.redis.password
    ),
}
executors = {
    'default': ThreadPoolExecutor(1),

}
scheduler = AsyncIOScheduler(
    jobstores=job_stores,
    executors=executors
)
