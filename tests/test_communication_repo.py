import pytest
from app.store.database.queries.communication import CommunicationRepo
from app.store.database.models import UsersMessages, Room, User
from datetime import datetime

from tests.conftest import add_and_commit


@pytest.fixture
def repo(session):
    return CommunicationRepo(session)

@pytest.mark.asyncio
async def test_insert_message(repo, session):
    room = Room(number=555333,
                name="room_32242",
                budget="200$")

    recipient = User(user_id=40000007,
                     username="User113253")

    sender = User(user_id=40000008,
                  username="User1413411")

    add_and_commit(session, room, recipient, sender)

    message = "Test message! Hello!"

    await repo.insert(room=room,
                      recipient_id=recipient.user_id,
                      sender_id=sender.user_id,
                      message=message)

    stored_message = session.query(UsersMessages).filter_by(room_id=room.id,
                                                            sender_id=sender.user_id,
                                                            recipient_id=recipient.user_id).first()

    assert stored_message is not None
    assert stored_message.message == message
    assert stored_message.recipient_id == recipient.user_id
    assert stored_message.sender_id == sender.user_id
    assert stored_message.room_id == room.id
    assert isinstance(stored_message.sent_at, datetime)
