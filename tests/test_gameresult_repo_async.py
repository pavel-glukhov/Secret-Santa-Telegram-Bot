import pytest
from sqlalchemy import select

from app.core.database.models import Room, User, GameResult
from app.core.database.repo.game_result import GameResultRepo
from tests.conftest import add_and_commit


# --- Constants for Test Data ---

# For test_insert_game_result
IGR_ROOM_NUMBER = 999333
IGR_ROOM_NAME = "insert_room_igr"
IGR_ROOM_BUDGET = "200$"
IGR_RECIPIENT_USER_ID = 40000001
IGR_RECIPIENT_USERNAME = "Recipient_IGR"
IGR_SENDER_USER_ID = 40000002
IGR_SENDER_USERNAME = "Sender_IGR"

# For test_get_recipient
TGR_ROOM_NUMBER = 888333
TGR_ROOM_NAME = "get_room_tgr"
TGR_ROOM_BUDGET = "200$"
TGR_RECIPIENT_USER_ID = 40000003
TGR_RECIPIENT_USERNAME = "User_Recipient_TGR"
TGR_SENDER_USER_ID = 40000004
TGR_SENDER_USERNAME = "User_Sender_TGR"

# For test_get_room_id_count
TRC_ROOM_NUMBER = 333222
TRC_ROOM_NAME = "get_room_trc"
TRC_ROOM_BUDGET = "200$"
TRC_USER1_ID = 6
TRC_USER1_USERNAME = "User1_TRC"
TRC_USER2_ID = 7
TRC_USER2_USERNAME = "User2_TRC"
TRC_USER3_ID = 8
TRC_USER3_USERNAME = "User3_TRC"
TRC_USER4_ID = 9
TRC_USER4_USERNAME = "User4_TRC"

# For test_get_sender
TGS_ROOM_NUMBER = 444222
TGS_ROOM_NAME = "get_room_tgs"
TGS_ROOM_BUDGET = "200$"
TGS_RECIPIENT_USER_ID = 40000005
TGS_RECIPIENT_USERNAME = "User_Recipient_TGS"
TGS_SENDER_USER_ID = 40000006
TGS_SENDER_USERNAME = "User_Sender_TGS"


# --- Core Fixture ---

@pytest.fixture
async def game_repo(session) -> GameResultRepo:
    """Fixture for the GameResultRepo."""
    return GameResultRepo(session)


# --- Fixtures for Entities (used by test_insert_game_result) ---

@pytest.fixture
async def igr_room(session) -> Room:
    """Creates and commits a Room for IGR tests."""
    room = Room(number=IGR_ROOM_NUMBER, name=IGR_ROOM_NAME, budget=IGR_ROOM_BUDGET)
    await add_and_commit(session, room)
    return room

@pytest.fixture
async def igr_recipient(session) -> User:
    """Creates and commits a recipient User for IGR tests."""
    user = User(user_id=IGR_RECIPIENT_USER_ID, username=IGR_RECIPIENT_USERNAME)
    await add_and_commit(session, user)
    return user

@pytest.fixture
async def igr_sender(session) -> User:
    """Creates and commits a sender User for IGR tests."""
    user = User(user_id=IGR_SENDER_USER_ID, username=IGR_SENDER_USERNAME)
    await add_and_commit(session, user)
    return user


# --- Fixtures for Entities (used by test_get_recipient) ---

@pytest.fixture
async def tgr_room(session) -> Room:
    """Creates and commits a Room for TGR tests."""
    room = Room(number=TGR_ROOM_NUMBER, name=TGR_ROOM_NAME, budget=TGR_ROOM_BUDGET)
    await add_and_commit(session, room)
    return room

@pytest.fixture
async def tgr_recipient(session) -> User:
    """Creates and commits a recipient User for TGR tests."""
    user = User(user_id=TGR_RECIPIENT_USER_ID, username=TGR_RECIPIENT_USERNAME)
    await add_and_commit(session, user)
    return user

@pytest.fixture
async def tgr_sender(session) -> User:
    """Creates and commits a sender User for TGR tests."""
    user = User(user_id=TGR_SENDER_USER_ID, username=TGR_SENDER_USERNAME)
    await add_and_commit(session, user)
    return user

@pytest.fixture
async def tgr_game_result(session, tgr_room: Room, tgr_recipient: User, tgr_sender: User) -> GameResult:
    """Creates and commits a GameResult for TGR tests."""
    # Note: GameResult.room_id stores the Room's primary key (tgr_room.id)
    game_result = GameResult(
        room_id=tgr_room.id,
        recipient_id=tgr_recipient.user_id,
        sender_id=tgr_sender.user_id
    )
    await add_and_commit(session, game_result)
    return game_result


# --- Fixtures for Entities (used by test_get_room_id_count) ---

@pytest.fixture
async def trc_room(session) -> Room:
    """Creates and commits a Room for TRC tests."""
    room = Room(number=TRC_ROOM_NUMBER, name=TRC_ROOM_NAME, budget=TRC_ROOM_BUDGET)
    await add_and_commit(session, room)
    return room

@pytest.fixture
async def trc_users(session) -> dict[int, User]:
    """Creates and commits multiple Users for TRC tests, returns a dict mapping ID to User."""
    users_data = [
        (TRC_USER1_ID, TRC_USER1_USERNAME),
        (TRC_USER2_ID, TRC_USER2_USERNAME),
        (TRC_USER3_ID, TRC_USER3_USERNAME),
        (TRC_USER4_ID, TRC_USER4_USERNAME),
    ]
    created_users_list = [User(user_id=uid, username=uname) for uid, uname in users_data]
    await add_and_commit(session, *created_users_list)
    return {user.user_id: user for user in created_users_list}

@pytest.fixture
async def trc_game_results(session, trc_room: Room, trc_users: dict[int, User]) -> list[GameResult]:
    """Creates and commits multiple GameResults for TRC tests."""
    # GameResult.room_id stores Room.id (PK)
    # User IDs are taken from the constants for clarity in pairing
    result1 = GameResult(
        room_id=trc_room.id,
        recipient_id=TRC_USER1_ID, # Uses ID directly as in original test logic
        sender_id=TRC_USER2_ID
    )
    result2 = GameResult(
        room_id=trc_room.id,
        recipient_id=TRC_USER3_ID,
        sender_id=TRC_USER4_ID
    )
    await add_and_commit(session, result1, result2)
    return [result1, result2]


# --- Fixtures for Entities (used by test_get_sender) ---

@pytest.fixture
async def tgs_room(session) -> Room:
    """Creates and commits a Room for TGS tests."""
    room = Room(number=TGS_ROOM_NUMBER, name=TGS_ROOM_NAME, budget=TGS_ROOM_BUDGET)
    await add_and_commit(session, room)
    return room

@pytest.fixture
async def tgs_recipient(session) -> User:
    """Creates and commits a recipient User for TGS tests."""
    user = User(user_id=TGS_RECIPIENT_USER_ID, username=TGS_RECIPIENT_USERNAME)
    await add_and_commit(session, user)
    return user

@pytest.fixture
async def tgs_sender(session) -> User:
    """Creates and commits a sender User for TGS tests."""
    user = User(user_id=TGS_SENDER_USER_ID, username=TGS_SENDER_USERNAME)
    await add_and_commit(session, user)
    return user

@pytest.fixture
async def tgs_game_result(session, tgs_room: Room, tgs_recipient: User, tgs_sender: User) -> GameResult:
    """Creates and commits a GameResult for TGS tests."""
    # Note: GameResult.room_id stores the Room's primary key (tgs_room.id)
    game_result = GameResult(
        room_id=tgs_room.id,
        recipient_id=tgs_recipient.user_id,
        sender_id=tgs_sender.user_id
    )
    await add_and_commit(session, game_result)
    return game_result


# --- Test Functions ---

@pytest.mark.asyncio
async def test_insert_game_result(
    game_repo: GameResultRepo,
    session,  # For direct DB verification
    igr_room: Room,
    igr_recipient: User,
    igr_sender: User
):
    """
    Tests that GameResultRepo.insert correctly creates a game result.
    It assumes repo.insert takes room.number as 'room_id'.
    """
    # Arrange (handled by fixtures)

    # Act: Call the repository method to insert the game result.
    # IMPORTANT: The original test implies game_repo.insert expects Room.number for room_id.
    inserted_game_result = await game_repo.insert(
        room_id=igr_room.number,  # Pass Room.number as per assumed repo logic
        recipient_id=igr_recipient.user_id,
        sender_id=igr_sender.user_id
    )

    # Assert: Check the returned GameResult object
    assert inserted_game_result is not None, "Repo did not return a GameResult object."
    assert inserted_game_result.recipient_id == igr_recipient.user_id, "Recipient ID mismatch."
    assert inserted_game_result.sender_id == igr_sender.user_id, "Sender ID mismatch."
    # Crucially, check that GameResult.room_id (FK) correctly refers to the Room's PK (igr_room.id)
    assert inserted_game_result.room_id == igr_room.id, \
        "GameResult.room_id does not match the actual room's primary key."

    # Assert: Verify directly from the database
    stmt = select(GameResult).filter_by(id=inserted_game_result.id) # Assuming GameResult has an 'id' PK
    db_result = await session.execute(stmt)
    stored_game_result = db_result.scalars().first()

    assert stored_game_result is not None, "GameResult not found in the database."
    assert stored_game_result.room_id == igr_room.id, "Stored room_id is incorrect."
    assert stored_game_result.recipient_id == igr_recipient.user_id, "Stored recipient_id is incorrect."
    assert stored_game_result.sender_id == igr_sender.user_id, "Stored sender_id is incorrect."


@pytest.mark.asyncio
async def test_get_recipient(
    game_repo: GameResultRepo,
    tgr_room: Room,
    tgr_recipient: User,
    tgr_sender: User,
    tgr_game_result: GameResult  # Fixture ensures GameResult exists
):
    """
    Tests GameResultRepo.get_recipient.
    It assumes repo.get_recipient takes Room.number as 'room_id' and sender's user_id.
    """
    # Arrange (handled by fixtures, tgr_game_result ensures the data is set up)
    assert tgr_game_result.room_id == tgr_room.id # Sanity check for fixture

    # Act: Fetch the recipient using the repository method.
    # IMPORTANT: Pass Room.number as room_id. user_id is the sender's ID.
    fetched_recipient = await game_repo.get_recipient(
        room_id=tgr_room.number,
        user_id=tgr_sender.user_id
    )

    # Assert
    assert fetched_recipient is not None, "Recipient User object was not fetched."
    assert isinstance(fetched_recipient, User), "Fetched object is not a User instance."
    assert fetched_recipient.user_id == tgr_recipient.user_id, "Fetched recipient user_id is incorrect."
    assert fetched_recipient.username == tgr_recipient.username, "Fetched recipient username is incorrect."


@pytest.mark.asyncio
async def test_get_room_id_count(
    game_repo: GameResultRepo,
    trc_room: Room,
    trc_users: dict[int, User],      # Fixture ensures users exist
    trc_game_results: list[GameResult] # Fixture ensures game results exist
):
    """
    Tests GameResultRepo.get_room_id_count.
    It assumes repo.get_room_id_count takes Room.number as 'room_id'.
    """
    # Arrange (handled by fixtures)
    assert len(trc_game_results) == 2, "Fixture setup for game results is incorrect."
    for gr in trc_game_results: # Sanity check
        assert gr.room_id == trc_room.id

    # Act: Get the count of game results for the specified room.
    # IMPORTANT: Pass Room.number as room_id.
    count = await game_repo.get_room_id_count(room_id=trc_room.number)

    # Assert
    assert count == 2, f"Expected count of 2 game results, but got {count}."


@pytest.mark.asyncio
async def test_get_sender(
    game_repo: GameResultRepo,
    tgs_room: Room,
    tgs_recipient: User,
    tgs_sender: User,
    tgs_game_result: GameResult  # Fixture ensures GameResult exists
):
    """
    Tests GameResultRepo.get_sender.
    It assumes repo.get_sender takes Room.number as 'room_id' and recipient's user_id.
    """
    # Arrange (handled by fixtures)
    assert tgs_game_result.room_id == tgs_room.id # Sanity check

    # Act: Fetch the sender using the repository method.
    # IMPORTANT: Pass Room.number as room_id. user_id is the recipient's ID.
    fetched_sender = await game_repo.get_sender(
        room_id=tgs_room.number,
        user_id=tgs_recipient.user_id
    )

    # Assert
    assert fetched_sender is not None, "Sender User object was not fetched."
    assert isinstance(fetched_sender, User), "Fetched object is not a User instance."
    assert fetched_sender.user_id == tgs_sender.user_id, "Fetched sender user_id is incorrect."
    assert fetched_sender.username == tgs_sender.username, "Fetched sender username is incorrect."

