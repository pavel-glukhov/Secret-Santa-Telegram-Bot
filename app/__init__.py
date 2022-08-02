from aiogram import Bot, Dispatcher, executor
import logging
from app.database.operations import UserDB, RoomDB, WishDB
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from app.settings import config

logging.basicConfig(level=logging.DEBUG)
bot = Bot(token=config.bot.token)
storage = MemoryStorage()
dispatcher = Dispatcher(bot, storage=storage)

user_db = UserDB
room_db = RoomDB
wish_db = WishDB

from app import handlers
