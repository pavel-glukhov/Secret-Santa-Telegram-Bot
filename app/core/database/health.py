import logging

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.core.database.sessions import get_session

logger = logging.getLogger(__name__)


async def check_database() -> bool:
    """
    Checks database availability using the application's session factory.
    Does NOT raise exceptions.
    """
    try:
        async with get_session() as session:
            await session.execute(text("SELECT 1"))

        logger.info("PostgreSQL connection OK")
        return True

    except SQLAlchemyError as e:
        logger.critical(
            "PostgreSQL is unavailable. "
            "Check database connection and configuration."
        )
        logger.debug("Database error details", exc_info=e)
        return False

    except Exception as e:
        logger.critical("Unexpected error during database health check")
        logger.debug("Unexpected DB error details", exc_info=e)
        return False
