import asyncio
import logging
import signal
from contextlib import suppress

from aiogram.exceptions import TelegramAPIError
from app.bot.loader import bot, dp
from app.core.app_init import init_application
from app.core.config.app_config import load_config, setup_logging
from app.core.scheduler import scheduler

logger = logging.getLogger(__name__)

class PollingApp:
    def __init__(self):
        self._stop_event = asyncio.Event()
        self._polling_task = None

    async def start(self):
        config = load_config()
        setup_logging(config)

        await init_application(config)

        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("Bot started in POLLING mode")

        self._polling_task = asyncio.create_task(dp.start_polling(bot), name="aiogram-polling")

        await self._stop_event.wait()
        logger.info("Shutdown signal received")

        await self.shutdown()

    async def shutdown(self):
        logger.info("Cancelling polling task")
        if self._polling_task:
            self._polling_task.cancel()
            with suppress(asyncio.CancelledError):
                await self._polling_task

        logger.info("Stopping scheduler")
        scheduler.shutdown(wait=False)

        logger.info("Closing bot session")
        await bot.session.close()
        logger.info("Polling shutdown completed")

    def stop(self):
        logger.info("Stop signal received")
        self._stop_event.set()

async def main():
    app = PollingApp()
    loop = asyncio.get_running_loop()

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, app.stop)
        except NotImplementedError:
            pass

    try:
        await app.start()
    except TelegramAPIError:
        logger.exception("Telegram API error")
    except Exception:
        logger.exception("Unexpected polling error")
    finally:
        logger.info("Exiting application")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
