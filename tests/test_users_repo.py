import pytest
from sqlalchemy.exc import IntegrityError

from app.store.database.models import User, Room
from app.store.database.repo.users import UserRepo

from tests.conftest import add_and_commit


@pytest.fixture
def user_repo(session):
    return UserRepo(session)

@pytest.fixture(scope='function')
def user(session):
    user = User(user_id=3000000,
                username="test_432562")
    try:
        add_and_commit(session, user)
    except IntegrityError:
        session.rollback()
    return user

@pytest.mark.asyncio
async def test_get_or_create_user(user_repo, session):
    user_id = 999999999
    user_data = {
        "username": "testuser",
        "language": "en",
        "first_name": "first_name_test_user",
        "last_name": "last_name_test_user",
        "is_active": True,
    }

    user, created = await user_repo.get_or_create(user_id, **user_data)
    assert created is True
    assert user.user_id == user_id
    assert user.username == "testuser"

    user, created = await user_repo.get_or_create(user_id)
    assert created is False

@pytest.mark.asyncio
async def test_get_user_or_none(user_repo, user):
    fetched_user = await user_repo.get_user_or_none(3000000)
    assert fetched_user is not None
    assert fetched_user.user_id == 3000000

    fetched_user = await user_repo.get_user_or_none("test_432562")
    assert fetched_user is not None
    assert fetched_user.username == "test_432562"

    assert await user_repo.get_user_or_none(0) is None

@pytest.mark.asyncio
async def test_update_user(user_repo, session, user):
    await user_repo.update_user(user_id=user.user_id,
                                first_name="first_name123",
                                last_name="last_name_123",
                                language="ru")

    updated_user = session.get(User, user.user_id)
    assert updated_user.language == "ru"
    assert updated_user.first_name == "first_name123"
    assert updated_user.last_name == "last_name_123"
@pytest.mark.asyncio
async def test_disable_enable_user(user_repo, session, user):
    await user_repo.disable_user(user.user_id)
    assert session.get(User, user.user_id).is_active is False

    await user_repo.enable_user(user.user_id)
    assert session.get(User, user.user_id).is_active is True

@pytest.mark.asyncio
async def test_get_user_language(user_repo, session):
    user = User(user_id=1000008, username="lang_user", language="es")
    add_and_commit(session, user)

    assert await user_repo.get_user_language(1000008) == "es"
    assert await user_repo.get_user_language(999) is None

@pytest.mark.asyncio
async def test_list_rooms_where_owner(user_repo, session):
    user = User(user_id=934055335, username="count_user_999442", language="es")
    room1 = Room(number=234523,
                 name="test_room1",
                 budget="200$",
                 owner_id=user.user_id)
    room2 = Room(number=532453,
                 name="test_room2",
                 budget="200$",
                 owner_id=user.user_id)

    add_and_commit(session, room1, room2, user)

    rooms = await user_repo.list_rooms_where_owner(user)
    assert len(rooms) == 2
    assert room1 in rooms
    assert room2 in rooms

@pytest.mark.asyncio
async def test_is_room_owner(user_repo, session, user):
    room = Room(number=324521,
                name="test_room3",
                budget="200$",
                owner_id=user.user_id)
    add_and_commit(session, room)

    assert await user_repo.is_room_owner(user, 324521) is True
    assert await user_repo.is_room_owner(user, 999999) is False


@pytest.mark.asyncio
async def test_delete_user(user_repo, session, user):
    await user_repo.delete_user(user.user_id)
    assert session.get(User, user.user_id) is None

