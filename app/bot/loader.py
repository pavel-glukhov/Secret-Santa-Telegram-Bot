from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from app.core.config.app_config import load_config

config = load_config()

bot = Bot(
    config.bot.token,
    default=DefaultBotProperties(
        parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())
