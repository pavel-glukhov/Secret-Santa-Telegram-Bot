import asyncio
import logging

from app import bot, config, dispatcher
from app.database import database_initialization
from app.logger import create_log_directory
from app.scheduler import scheduler

logger = logging.getLogger(__name__)

async def main():
    logger.info('-------------------')
    logger.info('Bot is started')
    logger.info('-------------------')
    await database_initialization()
    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    create_log_directory(config.log.log_path)
    scheduler.start()
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info('-------------------')
        logger.info('Bot has been stopped')
        logger.info('-------------------')
