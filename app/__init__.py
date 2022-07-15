from aiogram import Bot, Dispatcher, types
import logging

from app.settings import config

logging.basicConfig(level=logging.INFO)
bot = Bot(token=config.bot.token)
dispatcher = Dispatcher(bot)

from app.handlers import *
