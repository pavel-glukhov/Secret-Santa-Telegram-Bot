from contextlib import asynccontextmanager
from functools import lru_cache
from typing import AsyncGenerator, Optional

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import async_scoped_session

from app.config import load_config
from app.exceptions import DatabaseConfigError

config = load_config().db


def create_db_engine(postgres_url: str,
                     pool_size: int = 5,
                     max_overflow: int = 10) -> Optional[AsyncEngine]:
    try:
        return create_async_engine(
            postgres_url,
            pool_pre_ping=True,
            pool_size=pool_size,
            max_overflow=max_overflow,
            echo=False,
        )
    except Exception as ex:
        raise DatabaseConfigError(f"Couldn't create database engine: {str(ex)}")


try:
    pool_size = int(config.pool_size)
    max_overflow = int(config.max_overflow)
except (ValueError, TypeError) as e:
    raise DatabaseConfigError(f"Invalid pool_size or max_overflow values: {str(e)}") from e

engine = create_db_engine(config.postgres_url, pool_size=pool_size, max_overflow=max_overflow)


@lru_cache(maxsize=1)
def create_session_factory() -> sessionmaker:
    if engine is None:
        raise DatabaseConfigError("The database engine is not initialized.")
    return sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
        expire_on_commit=False,
        class_=AsyncSession
    )


def get_scoped_session() -> async_scoped_session:
    session_factory = create_session_factory()
    return async_scoped_session(session_factory, scopefunc=lambda: None)


@asynccontextmanager
async def get_session() -> AsyncGenerator[async_scoped_session, None]:
    session = get_scoped_session()
    try:
        yield session
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()
        await session.remove()
