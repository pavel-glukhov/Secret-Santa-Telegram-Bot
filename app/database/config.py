from tortoise import Tortoise

# TODO PSQL
# DATABASE_URL = 'postgresql+asyncpg://postgres:postgres@localhost/postgres'
DATABASE_URL = 'sqlite:db.db'


async def database_initialization():
    await Tortoise.init(
        db_url=DATABASE_URL,
        modules={'models': ['app.database.models']}
    )

