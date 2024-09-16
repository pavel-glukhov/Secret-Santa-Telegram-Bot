import logging

from aiogram import F, Router, types
from aiogram.filters import Command

from app.bot.keyborads.common import generate_inline_keyboard
from app.bot.languages import TranslationMainSchema

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data == 'menu_about_game')
@router.message(Command(commands=['about']))
async def about_game(data: types.Message | types.CallbackQuery, app_text_msg: TranslationMainSchema):
    message = data.message if isinstance(data, types.CallbackQuery) else data
    
    keyboard_inline = generate_inline_keyboard(
        {
            app_text_msg.buttons.return_back: "root_menu",
        }
    )
    message_text = app_text_msg.messages.main_menu.about_message
    
    await message.edit_text(text=message_text, reply_markup=keyboard_inline)
