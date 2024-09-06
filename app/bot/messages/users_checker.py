import asyncio
import logging

from aiogram.exceptions import (TelegramAPIError, TelegramForbiddenError,
                                TelegramRetryAfter)

from app.bot.loader import bot
from app.store.database.queries.users import UserRepo

logger = logging.getLogger(__name__)


async def checking_user_is_active(user_id, session):
    """
    Checking if a bot was blocked by user
    or user's chat is not existing by other reason.
    """
    try:
        await bot.send_chat_action(user_id, action='typing')
    
    except TelegramForbiddenError:
        logger.error(f"The bot was blocked by user [ID:{user_id}]")
        await UserRepo(session).disable_user(user_id)
        return False
    
    except TelegramRetryAfter as e:
        logger.error(
            f"Target [ID:{user_id}]: Flood limit is exceeded."
            f" Sleep {e.retry_after} seconds.")
        await asyncio.sleep(e.retry_after)
        return False
    
    except TelegramAPIError:
        logger.exception(f"Target [ID:{user_id}]: failed")
        return False
    
    return True
