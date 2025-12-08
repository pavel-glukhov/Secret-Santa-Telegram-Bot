from aiogram.exceptions import TelegramBadRequest
import logging

logger = logging.getLogger(__name__)


async def safe_delete_message(message: "types.Message", log_prefix: str = ""):
    """
    Attempts to safely delete a user or bot message.
    Logs a warning if the deletion fails, but does not interrupt execution.

    :param message: Message object
    :param log_prefix: Prefix for logging (e.g., 'process_wishes')
    """
    try:
        await message.delete()
    except TelegramBadRequest as e:
        logger.warning(f"{log_prefix} Could not delete message {message.message_id}: {e}")
    except Exception as e:
        logger.error(f"{log_prefix} Error while deleting message {message.message_id}: {e}")
