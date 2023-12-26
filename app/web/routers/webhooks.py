from aiogram import Bot, Dispatcher, types
from fastapi import APIRouter

from app.bot import bot
from app.bot import dispatcher as dp
from app.config import load_config, webhook_settings

router = APIRouter()
webhook_path = webhook_settings(load_config)['webhook_path']

@router.post(webhook_path)
async def bot_webhook(update: dict):
    telegram_update = types.Update(**update)
    Dispatcher.set_current(dp)
    Bot.set_current(bot)
    await dp.process_update(telegram_update)