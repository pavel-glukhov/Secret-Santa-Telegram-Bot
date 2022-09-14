import logging

from apscheduler.job import Job

from app.scheduler import scheduler
from typing import Callable
from datetime import datetime

logger = logging.getLogger(__name__)


# TODO форматирование для даты на логгер
async def add_task(task_func: Callable,
                   date_time: datetime,
                   task_id: str,
                   **kwargs) -> bool:
    """
    Add new task to job store.
    :param task_func:
    :param date_time:
    :param task_id:
    :param kwargs:
    :return:
    """
    scheduler.add_job(
        task_func,
        'date',
        run_date=date_time,
        kwargs=kwargs,
        id=str(task_id)
    )
    logger.info(f'New task {task_id} has been setup on {datetime}')
    return True


async def get_task(task_id: str) -> Job:
    """
    Get task from job store.
    :param task_id:
    :return: Task instance or False
    """
    task = scheduler.get_job(task_id)
    return task


async def remove_task(task_id: str) -> bool:
    """
    Remove task from job store.
    :param task_id:
    :return: bool
    """
    task = await get_task(task_id)
    if task:
        task.remove()
        logger.info(f'The task {task_id} has been removed.')
        return True
    logger.info(f'Request of is not existed {task_id} task.')
    return False
