from app.bot.middlewares.database_middleware import DatabaseMiddleware
from app.store.database.sessions import get_session


def register_middlewares(dp) -> None:
    dp.update.middleware(DatabaseMiddleware(get_session))
