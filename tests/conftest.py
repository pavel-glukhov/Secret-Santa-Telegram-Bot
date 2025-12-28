import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.database.models import Base

test_engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
TestSession = async_sessionmaker(bind=test_engine, expire_on_commit=False, class_=AsyncSession)

@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def session():
    async with TestSession() as session:
        yield session
        await session.close()

async def add_and_commit(session: AsyncSession, *entities):
    session.add_all(entities)
    await session.commit()