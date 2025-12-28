import pytest
from sqlalchemy import select
from app.core.database.repo.communication import CommunicationRepo
from app.core.database.models import UsersMessages, Room, User
from datetime import datetime

from tests.conftest import add_and_commit # Assuming this helper is well-defined

# --- Constants for test data ---
TEST_ROOM_NUMBER = 555333
TEST_ROOM_NAME = "room_32242"
TEST_ROOM_BUDGET = "200$"

TEST_RECIPIENT_USER_ID = 40000007
TEST_RECIPIENT_USERNAME = "User113253"

TEST_SENDER_USER_ID = 40000008
TEST_SENDER_USERNAME = "User1413411"

TEST_MESSAGE_CONTENT = "Test message! Hello!"


@pytest.fixture
async def repo(session):
    """Fixture for the CommunicationRepo."""
    return CommunicationRepo(session)


@pytest.fixture
async def test_room(session) -> Room:
    """Fixture to create and commit a test Room."""
    room = Room(
        number=TEST_ROOM_NUMBER,
        name=TEST_ROOM_NAME,
        budget=TEST_ROOM_BUDGET
    )
    await add_and_commit(session, room)
    return room


@pytest.fixture
async def test_recipient(session) -> User:
    """Fixture to create and commit a test recipient User."""
    recipient = User(
        user_id=TEST_RECIPIENT_USER_ID,
        username=TEST_RECIPIENT_USERNAME
    )
    await add_and_commit(session, recipient)
    return recipient


@pytest.fixture
async def test_sender(session) -> User:
    """Fixture to create and commit a test sender User."""
    sender = User(
        user_id=TEST_SENDER_USER_ID,
        username=TEST_SENDER_USERNAME
    )
    await add_and_commit(session, sender)
    return sender


@pytest.mark.asyncio
async def test_insert_message(
    repo: CommunicationRepo,
    session,
    test_room: Room,
    test_recipient: User,
    test_sender: User
):
    """
    Test that a message is correctly inserted into the database
    via the CommunicationRepo.
    """
    # 1. Act: Insert the message using the repository method
    await repo.insert(
        room=test_room,
        recipient_id=test_recipient.user_id,
        sender_id=test_sender.user_id,
        message=TEST_MESSAGE_CONTENT
    )

    # 2. Assert: Verify the message was stored correctly
    stmt = select(UsersMessages).filter_by(
        room_id=test_room.id,
        sender_id=test_sender.user_id,
        recipient_id=test_recipient.user_id,
        message=TEST_MESSAGE_CONTENT
    )
    result = await session.execute(stmt)
    stored_message = result.scalars().first()

    assert stored_message is not None, "Message was not found in the database."
    assert stored_message.message == TEST_MESSAGE_CONTENT
    assert stored_message.recipient_id == test_recipient.user_id
    assert stored_message.sender_id == test_sender.user_id
    assert stored_message.room_id == test_room.id
    assert isinstance(stored_message.sent_at, datetime), \
        f"Expected sent_at to be a datetime, got {type(stored_message.sent_at)}"
