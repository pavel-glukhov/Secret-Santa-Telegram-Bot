import logging

from aiogram import types
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware

# TODO Написать мидлваре на регистрацию пользователя.
from app.database import user_db

logger = logging.getLogger(__name__)


class UserMiddleware(BaseMiddleware):

    @staticmethod
    async def get(data: dict, user: types.User, message: types.Message):
        user_id = message.chat.id
        username = message.chat.username
        first_name = message.chat.first_name
        last_name = message.chat.last_name

        user, created = await user_db().get_or_create(
            user_id=user_id,
            username=username,
            first_name=first_name,
            last_name=last_name
        )
        if created:
            logger.info(f'The new user "{user_id}" has been created')

        return user, created

    async def on_pre_process_message(self, message: types.Message, data: dict):
        await self.get(data, message.from_user, message)
