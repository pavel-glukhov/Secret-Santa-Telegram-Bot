import asyncio
import logging

from app import bot, dispatcher
from app.database import database_initialization


async def main():
    logging.info('Running bot')
    await database_initialization()
    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
