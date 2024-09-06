from functools import lru_cache
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from app.config import load_config

engine = create_engine(load_config().db.postgres_url, pool_pre_ping=True)


@lru_cache
def create_session() -> scoped_session:
    session = scoped_session(
        sessionmaker(autocommit=False, autoflush=False, bind=engine)
    )
    return session


def get_session() -> Generator[scoped_session, None, None]:
    session = create_session()
    try:
        yield session
    finally:
        session.remove()
