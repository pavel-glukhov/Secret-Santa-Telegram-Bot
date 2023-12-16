import asyncio
import logging
from datetime import datetime
from typing import Callable

from apscheduler.job import Job

from app.store.scheduler import scheduler

logger = logging.getLogger(__name__)



# TODO Добавить semaphore
"""
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from asyncio import Lock

async def task():
    # Ваша асинхронная логика здесь
    pass

async def limited_task(semaphore):
    async with semaphore:
        await task()

async def main():
    scheduler = AsyncIOScheduler()

    # Создание семафора с максимальным количеством одновременно выполняемых задач
    semaphore = asyncio.Semaphore(1)

    # Запуск задачи с ограничением через семафор
    scheduler.add_job(limited_task, "interval", seconds=10, args=[semaphore])

    scheduler.start()

    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        scheduler.shutdown()

asyncio.run(main())

"""

def add_task(
        task_func: Callable,
        date_time: datetime,
        task_id: str,
        **kwargs
) -> Job:
    """
    Add new task to job store.
    :param task_func:
    :param date_time:
    :param task_id:
    :param kwargs:
    :return:
    """
    
    task = scheduler.add_job(
        task_func,
        'date',
        run_date=date_time,
        kwargs=kwargs,
        id=str(task_id)
    )
    logger.info(
        f'New task {task_id} has been setup on '
        f'{date_time.strftime("%Y-%b-%d, %H:%M:%S")}'
    )
    return task


def get_task(task_id: int) -> Job:
    """
    Get task from job store.
    :param task_id:
    :return: Task instance or False
    """
    task = scheduler.get_job(task_id)
    return task

def get_all_task() -> list[Job]:
    """
    Get all task from job store.
    :return: list of jobs
    """
    tasks = scheduler.get_jobs()
    return tasks

def remove_task(task_id: int) -> bool:
    """
    Remove task from job store.
    :param task_id:
    :return: bool
    """
    task = get_task(task_id)
    if task:
        task.remove()
        logger.info(f'The task [{task_id}] has been removed.')
        return True
    logger.info(f'The requested [{task_id}] task is not existed.')
    return False
