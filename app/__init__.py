import logging

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from app.config import config

logging.basicConfig(level=logging.DEBUG)
bot = Bot(token=config.bot.token)
storage = MemoryStorage()
dispatcher = Dispatcher(bot, storage=storage)

from app import handlers
