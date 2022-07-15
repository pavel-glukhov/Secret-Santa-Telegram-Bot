from aiogram import Bot, Dispatcher, types
import logging

from aiogram.contrib.fsm_storage.memory import MemoryStorage

from app.settings import config

logging.basicConfig(level=logging.INFO)
bot = Bot(token=config.bot.token)
storage = MemoryStorage()
dispatcher = Dispatcher(bot, storage=storage)

from app.handlers import *
