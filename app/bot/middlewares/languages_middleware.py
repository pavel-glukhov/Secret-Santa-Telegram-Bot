from typing import Callable, Generator

from aiogram import BaseMiddleware
from aiogram.types import Update
from sqlalchemy.orm import scoped_session

from app.bot.languages.loader import language_return_dataclass
from app.store.database.repo.users import UserRepo


class LanguageMiddleware(BaseMiddleware):
    """
    Middleware for handling user language.

    Arguments:
    redis_client -- Redis client for interacting with the Redis database.
    session_factory -- SQLAlchemy session factory for database interactions.

    Methods:
    __call__(handler, event, data) -- main method called on each event.
    _get_chat_id(event) -- helper method to get chat_id from the event.
    """

    def __init__(self, redis_client, session_factory: Callable[[
    ], Generator[scoped_session, None, None]]):
        super().__init__()
        self.redis_client = redis_client
        self.session_factory = session_factory

    async def __call__(self, handler, event: Update, data: dict):

        available_languages = self.redis_client().lrange("list_languages", 0, -1)
        chat_id = self._get_chat_id(event)

        async with self.session_factory() as session:
            if chat_id is not None:
                data['available_languages'] = available_languages
                user_language = await UserRepo(session).get_user_language(chat_id)
                if user_language:
                    data['lang'] = await language_return_dataclass(self.redis_client(), user_language)
                else:
                    data['lang'] = None

            return await handler(event, data)

    def _get_chat_id(self, event: Update):
        if event.message and event.message.chat:
            return event.message.chat.id
        elif event.callback_query and event.callback_query.from_user:
            return event.callback_query.from_user.id
        return None
