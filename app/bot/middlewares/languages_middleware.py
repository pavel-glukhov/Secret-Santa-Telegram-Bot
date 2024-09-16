import logging
from typing import Callable, Generator

from aiogram import BaseMiddleware
from aiogram.types import Update
from sqlalchemy.orm import scoped_session

from app.bot.languages import language_return_dataclass
from app.store.database.queries.users import UserRepo

logger = logging.getLogger(__name__)


class LanguageMiddleware(BaseMiddleware):
    def __init__(self, redis_client, session_factory: Callable[[], Generator[scoped_session, None, None]]):
        super().__init__()
        self.redis_client = redis_client
        self.session_factory = session_factory
    
    async def __call__(self, handler, event: Update, data: dict):
        session = next(self.session_factory())
        available_languages = self.redis_client().lrange("list_languages", 0, -1)
        
        if event.message and event.message.chat:
            chat_id = event.message.chat.id
        elif event.callback_query and event.callback_query.from_user:
            chat_id = event.callback_query.from_user.id
        else:
            chat_id = None
        
        if chat_id is not None:
            user_language = await UserRepo(session).get_user_language(chat_id)
            app_language = await language_return_dataclass(self.redis_client(), user_language)
            if not user_language:
                data['app_text_msg'] = None
                data['list_languages'] = available_languages
                return await handler(event, data)
            
            data['app_text_msg'] = app_language
            data['available_languages'] = available_languages
            return await handler(event, data)
        else:
            data['app_text_msg'] = None
            data['available_languages'] = available_languages
            return await handler(event, data)
