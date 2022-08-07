import asyncio
import logging

from tortoise import Tortoise

from app import bot, dispatcher
from app.database.config import database_initialization
from app.handlers.routers import (setup_cancel_handlers,
                                  setup_profile_handlers, setup_room_handlers,
                                  setup_root_handlers)


async def on_startup():
    logging.info("Register handlers...")
    setup_cancel_handlers(dispatcher)
    setup_root_handlers(dispatcher)
    setup_profile_handlers(dispatcher)
    setup_room_handlers(dispatcher)


async def main():
    await on_startup()
    await database_initialization()
    await Tortoise.generate_schemas()
    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
