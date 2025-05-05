from app.bot.middlewares.database_middleware import DatabaseMiddleware
from app.bot.middlewares.languages_middleware import LanguageMiddleware
from app.bot.middlewares.room_number_middleware import RoomNumberMiddleware
from app.store.database.sessions import get_session
from app.store.redis import get_redis_client


def register_middlewares(dp) -> None:
    dp.update.middleware(DatabaseMiddleware(get_session))
    dp.update.middleware(LanguageMiddleware(get_redis_client, get_session))
    dp.callback_query.middleware(RoomNumberMiddleware())