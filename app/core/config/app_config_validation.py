import sys
import logging

logger = logging.getLogger(__name__)

def validate_room_length_value(config) -> None:

    MIN_LENGTH = 5
    MAX_LENGTH = 8

    room_length = config.room.room_number_length

    if not (MIN_LENGTH <= room_length <= MAX_LENGTH):
        error_message = (
            f"Error: Invalid room number length set. "
            f"The 'ROOM_NUBER_LENGTH' must be between {MIN_LENGTH} and {MAX_LENGTH} (inclusive)."
        )
        logger.error(error_message)
        sys.exit(1)