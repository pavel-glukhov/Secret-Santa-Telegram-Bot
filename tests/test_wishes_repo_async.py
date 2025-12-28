import pytest
from sqlalchemy import select

from app.core.database.models import User, Room, WishRoom
from app.core.database.repo.wishes import WishRepo
from tests.conftest import add_and_commit


@pytest.fixture
async def wish_repo(session):
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

    await add_and_commit(session, wish, room, user)

    fetched_wish = await wish_repo.get(user_id=20012222, room_id=101101)
    assert fetched_wish == "Test wish"

    assert await wish_repo.get(user_id=9999, room_id=101101) is None
    assert await wish_repo.get(user_id=20012222, room_id=9999) is None


@pytest.mark.asyncio
async def test_create_or_update_wish(wish_repo, session):
    user = User(user_id=20022222, username="update_wish_user")
    room = Room(number=102102, name="WishUpdRoom",
                budget="200$",
                owner_id=user.user_id)

    await add_and_commit(session, room, user)

    await wish_repo.create_or_update_wish_for_room("New wish",
                                                   user_id=user.user_id,
                                                   room_id=room.number)
    result = await session.execute(
        select(WishRoom).filter_by(user_id=user.user_id, room_id=room.id)
    )
    created_wish = result.scalars().first()

    assert created_wish is not None
    assert created_wish.wish == "New wish"

    await wish_repo.create_or_update_wish_for_room("Updated wish",
                                                   user_id=user.user_id,
                                                   room_id=room.number)
    result = await session.execute(
        select(WishRoom).filter_by(user_id=user.user_id, room_id=room.id)
    )
    updated_wish = result.scalars().first()

    assert updated_wish.wish == "Updated wish"


@pytest.mark.asyncio
async def test_delete_wish(wish_repo, session):
    user = User(user_id=20220303,
                username="delete_wish_user")
    room = Room(number=103103,
                name="Wish Delete Room",
                owner_id=user.user_id,
                budget="200$")

    wish = WishRoom(user=user,
                    room=room,
                    wish="Delete this wish")

    await add_and_commit(session, room, user, wish)

    await wish_repo.delete(user_id=user.user_id,
                           room_id=room.id)
    result = await session.execute(
        select(WishRoom).filter_by(user_id=user.user_id, room_id=room.id)
    )
    deleted_wish = result.scalars().first()
    assert deleted_wish is None