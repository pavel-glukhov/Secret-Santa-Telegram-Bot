import asyncio
import logging

from app import bot, dispatcher
from app.database import database_initialization
from app.routers.room_routers import setup_room_handlers
from app.routers.profile_routers import setup_profile_handlers
from app.routers.root_routers import setup_cancel_handlers, setup_root_handlers


async def register_handlers():
    logging.info("Register handlers")

    setup_cancel_handlers(dispatcher)
    setup_root_handlers(dispatcher)
    setup_profile_handlers(dispatcher)
    setup_room_handlers(dispatcher)


async def main():
    await register_handlers()
    await database_initialization()
    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
