import logging

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ParseMode

from app.config import app_config


logging.basicConfig(level=logging.DEBUG)
bot = Bot(token=app_config().bot.token, parse_mode=ParseMode.HTML)
storage = MemoryStorage()
dispatcher = Dispatcher(bot, storage=storage)

from app.bot import handlers
