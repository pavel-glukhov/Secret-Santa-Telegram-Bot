import pytest
from app.store.database.models import User, Room
from app.store.database.queries.users import UserRepo

@pytest.fixture
def user_repo(session):
    return UserRepo(session)

def add_and_commit(session, *entities):
    session.add_all(entities)
    session.commit()

@pytest.mark.asyncio
async def test_get_or_create_user(user_repo, session):
    user_id = 1000001
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
async def test_get_user_or_none(user_repo, session):
    user = User(user_id=1000002, username="user2", language="fr")
    add_and_commit(session, user)

    fetched_user = await user_repo.get_user_or_none(1000002)
    assert fetched_user is not None
    assert fetched_user.user_id == 1000002

    fetched_user = await user_repo.get_user_or_none("user2")
    assert fetched_user is not None
    assert fetched_user.username == "user2"

    assert await user_repo.get_user_or_none(0) is None

@pytest.mark.asyncio
async def test_update_user(user_repo, session):
    user = User(user_id=1000003, username="user3", language="en")
    add_and_commit(session, user)

    await user_repo.update_user(user_id=1000003, username="updated_user3", language="ru")

    updated_user = session.get(User, 1000003)
    assert updated_user.username == "updated_user3"
    assert updated_user.language == "ru"

@pytest.mark.asyncio
async def test_disable_enable_user(user_repo, session):
    user = User(user_id=1000006, username="disable_user", is_active=True)
    add_and_commit(session, user)

    await user_repo.disable_user(1000006)
    assert session.get(User, 1000006).is_active is False

    await user_repo.enable_user(1000006)
    assert session.get(User, 1000006).is_active is True

@pytest.mark.asyncio
async def test_delete_user(user_repo, session):
    user = User(user_id=1000007, username="delete_user")
    add_and_commit(session, user)

    await user_repo.delete_user(1000007)
    assert session.get(User, 1000007) is None

@pytest.mark.asyncio
async def test_get_user_language(user_repo, session):
    user = User(user_id=1000008, username="lang_user", language="es")
    add_and_commit(session, user)

    assert await user_repo.get_user_language(1000008) == "es"
    assert await user_repo.get_user_language(999) is None

@pytest.mark.asyncio
async def test_list_rooms_where_owner(user_repo, session):
    user = User(user_id=1000009, username="owner_user_943")
    room1 = Room(number=234523, name="test_room1", budget="200$", owner_id=1000009)
    room2 = Room(number=532453, name="test_room2", budget="200$", owner_id=1000009)
    add_and_commit(session, user, room1, room2)

    rooms = await user_repo.list_rooms_where_owner(user)
    assert len(rooms) == 2
    assert room1 in rooms
    assert room2 in rooms

@pytest.mark.asyncio
async def test_is_room_owner(user_repo, session):
    user = User(user_id=1000010, username="owner_check")
    room = Room(number=324521, name="test_room3", budget="200$", owner_id=1000010)
    add_and_commit(session, user, room)

    assert await user_repo.is_room_owner(user, 324521) is True
    assert await user_repo.is_room_owner(user, 999999) is False
