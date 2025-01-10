import pytest
from app.store.database.models import User, Room, WishRoom
from app.store.database.queries.wishes import WishRepo
from tests.conftest import add_and_commit


@pytest.fixture
def wish_repo(session):
    return WishRepo(session)


@pytest.mark.asyncio
async def test_get_wish(wish_repo, session):
    user = User(user_id=20012222,
                username="wish_user")

    room = Room(number=101101,
                name="Wish Test Room",
                budget="200$",
                owner_id=20012222)

    wish = WishRoom(user=user,
                    room=room,
                    wish="Test wish")

    add_and_commit(session, wish, room, user)

    fetched_wish = await wish_repo.get(user_id=20012222, room_id=101101)
    assert fetched_wish == "Test wish"

    assert await wish_repo.get(user_id=9999, room_id=101) is None
    assert await wish_repo.get(user_id=2001, room_id=9999) is None


@pytest.mark.asyncio
async def test_create_or_update_wish(wish_repo, session):
    user = User(user_id=20022222, username="update_wish_user")
    room = Room(number=102102, name="WishUpdRoom",
                budget="200$",
                owner_id=user.user_id)

    add_and_commit(session, room, user)

    await wish_repo.create_or_update_wish_for_room("New wish",
                                                   user_id=user.user_id,
                                                   room_id=room.number)
    created_wish = session.query(WishRoom).filter_by(user_id=user.user_id,
                                                     room_id=room.id).first()

    assert created_wish is not None
    assert created_wish.wish == "New wish"

    await wish_repo.create_or_update_wish_for_room("Updated wish",
                                                   user_id=user.user_id,
                                                   room_id=room.number)
    updated_wish = session.query(WishRoom).filter_by(user_id=user.user_id,
                                                     room_id=room.id).first()

    assert updated_wish.wish == "Updated wish"


@pytest.mark.asyncio
async def test_delete_wish(wish_repo, session):
    user = User(user_id=20220303,
                username="delete_wish_user")
    room = Room(number=103103,
                name="Wish Delete Room",
                owner_id=2003,
                budget="200$")

    wish = WishRoom(user=user,
                    room=room,
                    wish="Delete this wish")

    add_and_commit(session, room, wish)

    await wish_repo.delete(user_id=2003,
                           room_id=103)
    deleted_wish = session.query(WishRoom).filter_by(user_id=2003,
                                                     room_id=3).first()
    assert deleted_wish is None
