from aiogram import Dispatcher

from app.handlers.profiles.common import my_profile


def setup_profile_handlers(dp: Dispatcher):
    dp.register_message_handler(my_profile, lambda
        message: message.text == "Мой профиль 👤")
