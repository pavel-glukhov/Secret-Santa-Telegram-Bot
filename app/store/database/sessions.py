from contextlib import contextmanager
from functools import lru_cache
from typing import Generator, Optional

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import scoped_session, sessionmaker

from app.config import load_config
from app.exceptions import DatabaseConfigError

config = load_config().db

def create_db_engine(postgres_url: str,
                     pool_size: int = 5,
                     max_overflow: int = 10) -> Optional[Engine]:

    try:
        return create_engine(
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
    )

def get_scoped_session() -> scoped_session:
    session_factory = create_session_factory()
    return scoped_session(session_factory)

@contextmanager
def get_session() -> Generator[scoped_session, None, None]:
    session = get_scoped_session()
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.remove()