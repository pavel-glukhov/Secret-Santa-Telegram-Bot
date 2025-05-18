import asyncio
from logging.config import fileConfig

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import pool
from alembic import context

from app.store.database.models import Base
from app.config import load_config

config = context.config
section = config.config_ini_section

config.set_section_option(section, "DB_USER", load_config().db.user)
config.set_section_option(section, "DB_PASS", load_config().db.password)
config.set_section_option(section, "DB_HOST", load_config().db.host)
config.set_section_option(section, "DB_NAME", load_config().db.name)
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

async def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an AsyncEngine
    and associate a connection with the context.
    """
    connectable = create_async_engine(
        config.get_main_option("sqlalchemy.url"),
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(lambda conn: context.configure(
            connection=conn, target_metadata=target_metadata
        ))

        with context.begin_transaction():
            context.run_migrations()

    await connectable.dispose()

async def main():
    if context.is_offline_mode():
        await run_migrations_offline()
    else:
        await run_migrations_online()

if __name__ == "__main__":
    asyncio.run(main())