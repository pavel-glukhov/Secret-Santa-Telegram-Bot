import asyncio
import logging

from aiogram.exceptions import (TelegramAPIError, TelegramBadRequest,
                                TelegramForbiddenError, TelegramRetryAfter)
from aiohttp import ClientError

from app.bot.loader import bot
from app.core.database.repo.users import UserRepo

logger = logging.getLogger(__name__)


async def checking_user_is_active(user_id: int, session) -> bool:
    """
    Checking if a bot was blocked by user
    or user's chat is not existing by other reason.

    :param user_id: ID of the user to check.
    :param session: Database session.
    :return: True if the user is active, False otherwise.
    """
    try:
        await bot.send_chat_action(user_id, action='typing')
    
    except TelegramBadRequest as e:
        logger.error(f"Target [ID:{user_id}]: checking is failed")
        logger.error(f"user checker: {e.message}")
        return False
    
    except TelegramForbiddenError:
        logger.error(f"The bot was blocked by user [ID:{user_id}]")
        await UserRepo(session).disable_user(user_id)
        return False
    
    except TelegramRetryAfter as e:
        logger.error(
            f"Target [ID:{user_id}]: Flood limit is exceeded. Sleep {e.retry_after} seconds.")
        await asyncio.sleep(e.retry_after)
        return False
    
    except ClientError:
        logger.error(f"Target [ID:{user_id}]: Network error occurred.")
        await asyncio.sleep(5)
        return False
    
    except TelegramAPIError:
        logger.exception(f"Target [ID:{user_id}]: checking is failed")
        return False
    return True
