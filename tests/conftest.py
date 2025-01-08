import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from app.store.database.models import Base, User

test_engine = create_engine("sqlite:///:memory:")
TestSession = scoped_session(sessionmaker(bind=test_engine))

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(test_engine)
    yield
    Base.metadata.drop_all(test_engine)

@pytest.fixture
def session():
    session = TestSession()
    yield session
    session.close()

def add_and_commit(session, *entities):
    session.add_all(entities)
    session.commit()
