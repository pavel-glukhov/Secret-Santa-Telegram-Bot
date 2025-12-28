import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.database import Base

# Создаем асинхронный движок для тестовой базы данных SQLite
test_engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
TestSession = async_sessionmaker(bind=test_engine, expire_on_commit=False, class_=AsyncSession)

@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    """
    Фикстура для создания и удаления тестовой базы данных
    """
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def session():
    """
    Фикстура для предоставления асинхронной сессии
    """
    async with TestSession() as session:
        yield session
        await session.close()

async def add_and_commit(session: AsyncSession, *entities):
    """
    Вспомогательная функция для добавления и коммита сущностей
    """
    session.add_all(entities)
    await session.commit()