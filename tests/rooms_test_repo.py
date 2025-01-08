import pytest
from app.store.database.models import Room, User
from app.store.database.queries.rooms import RoomRepo


@pytest.fixture
def room_repo(session):
    return RoomRepo(session)

def add_and_commit(session, *entities):
    session.add_all(entities)
    session.commit()


@pytest.mark.asyncio
async def test_create_room(room_repo, session):
    user = User(user_id=1000001, username="owner")
    add_and_commit(session, user)

    room = await room_repo.create(name="Room1",
                                  owner_id=1000001,
                                  budget="100$",
                                  user_wish="Books")

    assert room is not None
    assert room.name == "Room1"
    assert room.budget == "100$"
    assert room.owner_id == 1000001
    assert len(room.members) == 1
    assert room.members[0] == user


@pytest.mark.asyncio
async def test_update_room(room_repo, session):
    room = Room(name="Room2",
                owner_id=1000001,
                budget="100$",
                number=100102,
                )
    add_and_commit(session, room)

    room = session.query(Room).filter_by(name='Room2').first()

    await room_repo.update(room_number=room.number, name="Updated_name", budget="150$")
    updated_room = session.query(Room).filter_by(name="Updated_name").first()

    assert updated_room is not None
    assert updated_room.name == "Updated_name"
    assert updated_room.budget == "150$"


@pytest.mark.asyncio
async def test_add_member(room_repo, session):
    user = User(user_id=1000002, username="member")
    room = Room(name="Room_add_tst", budget="200", owner_id=1000001, number=100103)
    add_and_commit(session, user, room)


    room = session.query(Room).filter_by(name='Room_add_tst').first()
    result = await room_repo.add_member(user_id=1000002, room_number=room.number)

    assert result is True
    assert user in room.members

@pytest.mark.asyncio
async def test_remove_member(room_repo, session):
    user = User(user_id=1000003, username="member2")
    room = Room(name="Room3", number=98765, budget="300", owner_id=1000003)
    room.members.append(user)
    add_and_commit(session, user, room)

    await room_repo.remove_member(user_id=1000003, room_number=98765)
    assert user not in room.members

@pytest.mark.asyncio

async def test_is_member(room_repo, session):
    user = User(user_id=1000004, username="testuser")

    room = Room(name="Room4", number=13579, budget="400$", owner_id=1000004)
    room.members.append(user)
    add_and_commit(session, user, room)

    assert await room_repo.is_member(user_id=1000004, room_number=13579) is True
    assert await room_repo.is_member(user_id=1000099, room_number=13579) is False


@pytest.mark.asyncio
async def test_is_room_owner(room_repo, session):
    room = Room(name="Room5", number=24680, budget="500$", owner_id=1000001)
    add_and_commit(session,  room)

    assert await room_repo.is_owner(user_id=1000001, room_number=24680) is True
    assert await room_repo.is_owner(user_id=1000002, room_number=24680) is False

@pytest.mark.asyncio
async def test_delete_room(room_repo, session):
    room = Room(name="Room6", number=111222, budget="600", owner_id=1000001)
    add_and_commit(session,  room)

    assert await room_repo.delete(room_number=111222) is True
    assert session.query(Room).filter_by(number=111222).first() is None
