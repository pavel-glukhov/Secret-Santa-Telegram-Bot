import asyncio

from app import dispatcher, bot
from app.database.config import engine, Base


async def main():
    # async with engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.drop_all)
    #     await conn.run_sync(Base.metadata.create_all)
    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
