from app.logger import logger
from app.scheduler import scheduler


# TODO форматирование для даты на логгер
async def add_task(task_func, datetime, task_id, **kwargs):
    scheduler.add_job(
        task_func,
        'date',
        run_date=datetime(datetime),
        kwargs=kwargs,
        id=str(task_id)
    )
    logger.info(f'New task {task_id} has been setup on {datetime}')
    return True


async def get_task(task_id):
    """
    Get task
    :param task_id:
    :return: Task instance or False
    """
    task = scheduler.get_job(task_id)
    return task


async def remove_task(task_id):
    """
    Remove task from job store
    :param task_id:
    :return:
    """
    task = await get_task(task_id)
    if task:
        task.remove()
        logger.info(f'The task {task_id} has been removed')
        return True
    return False
