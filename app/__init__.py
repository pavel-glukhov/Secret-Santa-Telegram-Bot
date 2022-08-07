import logging

from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from app.settings import config

logging.basicConfig(level=logging.DEBUG)
bot = Bot(token=config.bot.token)
storage = MemoryStorage()
dispatcher = Dispatcher(bot, storage=storage)

from app import handlers
