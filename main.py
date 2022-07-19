import asyncio

from tortoise import Tortoise

from app import dispatcher, bot
from app.database.config import database_initialization


async def main():
    await database_initialization()
    await Tortoise.generate_schemas()
    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
