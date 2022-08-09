from aiogram import Dispatcher
from aiogram.dispatcher.filters import Text

from app.handlers.common import about_game, cancel_handler, start
from app.keyborads.constants import MAIN_REPLY_BUTTONS


def setup_cancel_handlers(dp: Dispatcher):
    # cancel handlers
    dp.register_message_handler(
        cancel_handler, Text(contains=[x for x in MAIN_REPLY_BUTTONS.values()]),
        state='*'
    )
    dp.register_message_handler(
        cancel_handler,
        state='*', commands='отмена'
    )
    dp.register_message_handler(
        cancel_handler, Text(equals='отмена',
                             ignore_case=True),
        state='*'
    )


def setup_root_handlers(dp: Dispatcher):
    # common root handlers
    dp.register_message_handler(
        start, commands=['start']
    )
    dp.register_message_handler(
        about_game,
        lambda message: message.text == MAIN_REPLY_BUTTONS['about']
    )
