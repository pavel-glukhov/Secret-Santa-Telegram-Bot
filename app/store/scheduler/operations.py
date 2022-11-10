import logging
from datetime import datetime
from typing import Callable

from apscheduler.job import Job

from app.store.scheduler import scheduler

logger = logging.getLogger(__name__)


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


def remove_task(task_id: int) -> bool:
    """
    Remove task from job store.
    :param task_id:
    :return: bool
    """
    task = get_task(task_id)
    if task:
        task.remove()
        logger.info(f'The task {task_id} has been removed.')
        return True
    logger.info(f'Request of is not existed {task_id} task.')
    return False
