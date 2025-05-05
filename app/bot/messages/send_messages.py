import asyncio
import logging

from aiogram.exceptions import (TelegramAPIError, TelegramBadRequest,
                                TelegramForbiddenError, TelegramNotFound,
                                TelegramRetryAfter, TelegramServerError,
                                TelegramUnauthorizedError)
from aiohttp import ClientError

from app.bot.loader import bot

logger = logging.getLogger(__name__)


async def send_message(user_id: int,
                       text: str,
                       disable_notification: bool = False,
                       max_retries: int = 3,
                       **kwargs) -> bool:
    if len(text) > 4096:
        logger.error(f"Text too long: {len(text)} characters. Telegram limit is 4096")
        return False

    retry_count = 0
    while retry_count <= max_retries:
        try:
            valid_kwargs = {'reply_markup', 'parse_mode', 'disable_web_page_preview', 'entities'}
            filtered_kwargs = {k: v for k, v in kwargs.items() if k in valid_kwargs}
            await bot.send_message(user_id, text, disable_notification=disable_notification, **filtered_kwargs)
            logger.info(f"Message sent [ID:{user_id}]: successful")
            return True

        except TelegramForbiddenError:
            logger.error(f"Target [ID:{user_id}]: blocked by user")
            return False

        except TelegramRetryAfter as e:
            if retry_count >= max_retries:
                logger.error(f"Target [ID:{user_id}]: Retry limit reached")
                return False

            logger.warning(f"Target [ID:{user_id}]: Too many requests. Waiting {e.retry_after} seconds")
            await asyncio.sleep(e.retry_after)
            await asyncio.sleep(0.05)

        except TelegramBadRequest:
            logger.error(f"Target [ID:{user_id}]: Invalid request")
            return False

        except TelegramNotFound:
            logger.error(f"Target [ID:{user_id}]: User or chat not found")
            return False

        except TelegramUnauthorizedError:
            logger.error(f"Target [ID:{user_id}]: Invalid token or bot deleted")
            return False

        except TelegramServerError:
            if retry_count >= max_retries:
                logger.error(f"Target [ID:{user_id}]: Telegram server error. Retry limit reached")
                return False

            logger.warning(f"Target [ID:{user_id}]: Telegram server error. Retrying with exponential backoff")
            await asyncio.sleep(min(2 ** retry_count, 60))
        except ClientError:
            if retry_count >= max_retries:
                logger.error(f"Target [ID:{user_id}]: Network error. Retry limit reached")
                return False

            logger.warning(f"Target [ID:{user_id}]: Network error. Retrying with exponential backoff")
            await asyncio.sleep(min(1.5 ** retry_count, 30))
        except TelegramAPIError:
            logger.exception(f"Target [ID:{user_id}]: Unknown API error")
            return False

        except Exception as e:
            logger.exception(f"Target [ID:{user_id}]: Unexpected error: {str(e)}")
            return False

        retry_count += 1


async def broadcaster(list_users: list) -> None:
    """
    Broadcast messages to a list of users.
    :param list_users: List of users to send messages to.
    """
    if not list_users or not isinstance(list_users, list):
        logger.error("Invalid or empty user list")
        return
    stats = {
        'total': len(list_users),
        'successful': 0,
        'failed': 0,
        'errors': {}
    }
    tasks = []
    try:
        for user in list_users:
            if (not isinstance(user, dict)
                    or 'user_id' not in user
                    or 'text' not in user):
                logger.error(f"Incorrect user data: {user}")
                continue
            tasks.append(send_message(user_id=user['user_id'],
                                      text=user['text'],
                                      reply_markup={user['player_language'].buttons.menu: "start_menu"}))
            await asyncio.sleep(.05)  # 20 messages per second
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for result in results:
            if result is True:
                stats['successful'] += 1
            elif result is False:
                stats['failed'] += 1
            else:
                stats['failed'] += 1
                error_str = str(result)
                stats['errors'][str(result)] = stats['errors'].get(str(result), 0) + 1
                logger.error(f"Error during of sending data:: {error_str}")
    finally:
        logger.info(f"Sanding statistics: {stats}")
