import pytest
from sqlalchemy.exc import IntegrityError

from app.store.database.models import Room, User
from app.store.database.queries.rooms import RoomRepo
from tests.conftest import add_and_commit


@pytest.fixture
def room_repo(session):
    return RoomRepo(session)


@pytest.mark.asyncio
async def test_create_room(room_repo, session):
    user = User(user_id=4000999, username="test_432532")
    add_and_commit(session, user)
    room = await room_repo.create(name="Room1",
                                  owner_id=user.user_id,
                                  budget="100$",
                                  user_wish="Books")

    assert room is not None
    assert room.name == "Room1"
    assert room.budget == "100$"
    assert room.owner_id == user.user_id
    assert len(room.members) == 1
    assert room.members[0] == user


@pytest.mark.asyncio
async def test_update_room(room_repo, session):
    user = User(user_id=4000001, username="test_132562")
    room = Room(name="room_update_test",
                owner_id=4000001,
                budget="100$",
                number=100102,
                )
    add_and_commit(session, room, user)

    room = session.query(Room).filter_by(name='room_update_test').first()

    await room_repo.update(room_number=room.number,
                           name="updated_name", budget="150$")
    updated_room = session.query(Room).filter_by(name="updated_name").first()

    assert updated_room is not None
    assert updated_room.name == "updated_name"
    assert updated_room.budget == "150$"


@pytest.mark.asyncio
async def test_add_member(room_repo, session):
    user = User(user_id=4000002, username="test_135562")
    room = Room(name="room_add_tst",
                budget="200",
                owner_id=4000002,
                number=100103)
    add_and_commit(session, room, user)

    room = session.query(Room).filter_by(name='room_add_tst').first()
    result = await room_repo.add_member(user_id=4000002,
                                        room_number=room.number)

    assert result is True
    for member in room.members:
        assert 4000002 == member.user_id


@pytest.mark.asyncio
async def test_remove_member(room_repo, session):
    user = User(user_id=4000003, username="test_135563")
    new_member = User(user_id=23423346,
                      username="test_43345362")
    room = Room(name="room_remove_test",
                number=938765,
                budget="300",
                owner_id=4000003)

    room.members.append(new_member)
    add_and_commit(session, new_member, room, user)

    await room_repo.remove_member(user_id=23423346,
                                  room_number=938765)

    session.refresh(room)
    assert all(member.user_id != new_member.user_id for member in room.members)

@pytest.mark.asyncio
async def test_is_member(room_repo, session):
    user = User(user_id=4000004, username="test_235563")
    new_member = User(user_id=25531246,
                      username="test_4252352")
    room = Room(name="room_is_member_test",
                number=13579,
                budget="400$",
                owner_id=4000004)

    room.members.append(new_member)
    add_and_commit(session,new_member, room, user)

    assert await room_repo.is_member(user_id=25531246,
                                     room_number=13579) is True
    assert await room_repo.is_member(user_id=2000099,
                                     room_number=13579) is False
#
#
@pytest.mark.asyncio
async def test_is_room_owner(room_repo, session):
    user = User(user_id=4000005, username="test_235876")
    is_no_member = User(user_id=25531646,
                      username="test_423452")
    room = Room(name="room_is_owner_test",
                number=24680,
                budget="500$",
                owner_id=4000005)

    add_and_commit(session,  is_no_member, room, user)

    assert await room_repo.is_owner(user_id=4000005,
                                    room_number=24680) is True
    assert await room_repo.is_owner(user_id=25531646,
                                    room_number=24680) is False

@pytest.mark.asyncio
async def test_delete_room(room_repo, session):
    user = User(user_id=4000006, username="test_233876")
    room = Room(name="room_delete_test",
                number=111222, budget="600",
                owner_id=4000006)
    add_and_commit(session,  room, user)

    assert await room_repo.delete(room_number=111222) is True
    assert session.query(Room).filter_by(number=111222).first() is None
