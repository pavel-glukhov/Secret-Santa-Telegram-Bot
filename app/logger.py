import logging
import os
from logging import Handler
from logging.handlers import TimedRotatingFileHandler

from app import config

FORMATTER = u'%(asctime)s\t%(levelname)s\t%(filename)s:%(lineno)d\t%(message)s'


def create_log_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def app_handler(path):
    handler = TimedRotatingFileHandler(
        os.path.join(config.log.log_path, path),
        when="midnight",
        interval=1,
        encoding='utf-8',
        backupCount=14
    )
    formatter = logging.Formatter(FORMATTER)
    handler.setFormatter(formatter)
    return handler


def app_logging():
    path = os.path.join(config.log.log_path, 'logs.txt')
    app_logger = logging.getLogger(__name__)
    app_logger.setLevel(logging.INFO)

    app_logger.addHandler(app_handler(path))
    app_loggers = [
        logging.getLogger("tortoise"),
        logging.getLogger("asyncpg")
    ]
    for log in app_loggers:
        log.addHandler(app_handler(path))

    return app_logger


logger = app_logging()
