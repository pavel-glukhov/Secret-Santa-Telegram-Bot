import logging
from datetime import datetime
from typing import Callable

from apscheduler.job import Job

from app.store.scheduler import scheduler

logger = logging.getLogger(__name__)


class TaskScheduler:
    def __init__(self):
        """
        Initialize TaskScheduler with a scheduler instance.
        """
        self.scheduler = scheduler

    def add_task(
            self,
            task_func: Callable,
            date_time: datetime,
            task_id: str,
            **kwargs
    ) -> Job:
        """
        Add new task to job store.

        :param task_func: Function to be scheduled
        :param date_time: Datetime when task should run
        :param task_id: Unique identifier for the task
        :param kwargs: Additional arguments for task_func
        :return: Scheduled Job instance
        """
        task = self.scheduler.add_job(
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

    def get_task(self, task_id: int) -> Job:
        """
        Get task from job store.

        :param task_id: Task identifier
        :return: Task instance or None if not found
        """
        return self.scheduler.get_job(str(task_id))

    def get_all_tasks(self) -> list[Job]:
        """
        Get all tasks from job store.

        :return: List of Job instances
        """
        return self.scheduler.get_jobs()

    def remove_task(self, task_id: int) -> bool:
        """
        Remove task from job store.

        :param task_id: Task identifier
        :return: True if task was removed, False if task not found
        """
        task = self.get_task(task_id)
        if task:
            task.remove()
            logger.info(f'The task [{task_id}] has been removed.')
            return True
        logger.info(f'The requested [{task_id}] task does not existed.')
        return False
