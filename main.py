import asyncio
import logging.config
import os

import yaml

from app.bot import bot, app_config, dispatcher
from app.config import root_path
from app.store.database import database_initialization
from app.store.scheduler import scheduler

logger = logging.getLogger(__name__)


def create_directory(path: str) -> None:
    if not os.path.exists(path):
        os.makedirs(path)


def setup_logging() -> None:
    config = app_config()
    create_directory(config.log.log_path)
    configuration_file = os.path.join(root_path, config.log.config_file)
    
    with open(configuration_file, 'r') as stream:
        logging_cfg = yaml.load(stream, Loader=yaml.FullLoader)
    
    logging_cfg['handlers']['timed_rot_handler']['filename'] = os.path.join(
        config.log.log_path,
        config.log.log_file
    )
    logging.config.dictConfig(logging_cfg)


async def main():
    logger.info('Starting scheduler...')
    scheduler.start()
    logger.info('Starting database initialization...')
    await database_initialization()
    logger.info('Bot starting...')
    await dispatcher.start_polling(bot)

if __name__ == "__main__":
    try:
        setup_logging()
        asyncio.run(main())
    
    except (KeyboardInterrupt, SystemExit):
        logger.info('Bot has been stopped')
