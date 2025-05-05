import pytest

from tests.conftest import add_and_commit
from app.store.database.models import Room, User, GameResult
from app.store.database.repo.game_result import GameResultRepo


@pytest.fixture
def game_repo(session):
    return GameResultRepo(session)


@pytest.mark.asyncio
async def test_insert_game_result(game_repo, session):
    room = Room(number=999333, name="insert_room_1234", budget="200$")
    recipient = User(user_id=40000001, username="Recipient")
    sender = User(user_id=400000002, username="Sender")
    add_and_commit(session, room, recipient, sender)

    result = await game_repo.insert(room_id=999333,
                                    recipient_id=40000001,
                                    sender_id=400000002)

    assert result is not None
    assert result.recipient_id == recipient.user_id
    assert result.sender_id == sender.user_id


#
@pytest.mark.asyncio
async def test_get_recipient(game_repo, session):
    room = Room(number=888333, name="get_room_214", budget="200$")
    recipient = User(user_id=40000003, username="User_42452")
    sender = User(user_id=40000004, username="User_524523")
    add_and_commit(session, room)

    result = GameResult(room_id=room.id,
                        recipient_id=recipient.user_id,
                        sender_id=sender.user_id)

    add_and_commit(session, recipient, sender, result)

    fetched_recipient = await game_repo.get_recipient(room_id=888333,
                                                      user_id=sender.user_id)
    assert fetched_recipient is not None
    assert fetched_recipient.user_id == recipient.user_id


@pytest.mark.asyncio
async def test_get_room_id_count(game_repo, session):
    room = Room(number=333222, name="get_room_2144", budget="200$")
    add_and_commit(session, room)
    result1 = GameResult(room_id=room.id,
                         recipient_id=6,
                         sender_id=7)
    result2 = GameResult(room_id=room.id,
                         recipient_id=8,
                         sender_id=9)
    add_and_commit(session, result1, result2)

    count = await game_repo.get_room_id_count(room_id=333222)

    assert count == 2


@pytest.mark.asyncio
async def test_get_sender(game_repo, session):
    room = Room(number=444222,
                name="get_room_23514",
                budget="200$")
    recipient = User(user_id=40000005,
                     username="User1033")
    sender = User(user_id=40000006,
                  username="User14521")

    add_and_commit(session, room, recipient, sender)

    result = GameResult(room_id=room.id,
                        recipient_id=recipient.user_id,
                        sender_id=sender.user_id)

    add_and_commit(session, result)

    fetched_sender = await game_repo.get_sender(room_id=444222, user_id=40000005)

    assert fetched_sender is not None
    assert fetched_sender.user_id == sender.user_id
