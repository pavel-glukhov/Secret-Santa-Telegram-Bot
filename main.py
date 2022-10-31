import asyncio
import logging.config
import os

import yaml

from app.bot import bot, config, dispatcher
from app.config import root_path
from app.store.database import database_initialization
from app.store.scheduler import scheduler

logger = logging.getLogger(__name__)


def create_directory(path: str) -> None:
    if not os.path.exists(path):
        os.makedirs(path)


def setup_logging() -> None:
    create_directory(config.log.log_path)
    configuration_file = os.path.join(root_path, config.log.config_file)

    with open(configuration_file, 'r') as stream:
        logging_config = yaml.load(stream, Loader=yaml.FullLoader)

    logging_config['handlers']['timed_rotating_handler'][
        'filename'] = os.path.join(
        config.log.log_path,
        config.log.log_file
    )

    logging.config.dictConfig(logging_config)


async def main():
    logger.info('-------------------')
    logger.info('Bot starting...')
    logger.info('-------------------')
    await database_initialization()
    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    setup_logging()
    scheduler.start()
    try:
        asyncio.run(main())

    except (KeyboardInterrupt, SystemExit):
        logger.info('-------------------')
        logger.info('Bot has been stopped')
        logger.info('-------------------')
