import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode

from app import dispatcher as dp
from app.database import room_db
from app.database.models import User
from app.keyborads.common import generate_inline_keyboard

logger = logging.getLogger(__name__)


class ChangeOwner(StatesGroup):
    waiting_for_owner_name = State()


async def change_room_owner(message: types.Message, room_number):
    await ChangeOwner.waiting_for_owner_name.set()
    state = dp.get_current().current_state()
    await state.update_data(room_number=room_number)

    keyboard_inline = generate_inline_keyboard(
        {
            "Отмена": 'cancel'
        }
    )

    await message.answer(
        'Хочешь поменять владельца комнаты?\n'
        'Новый владелец комнаты должен являться ее участником. '
        '*Учти, что ты потеряешь контроль за комнатой.*\n\n'
        '*Для смены владельца, напиши его ник.*\n',
        reply_markup=keyboard_inline
    )


@dp.message_handler(state=ChangeOwner.waiting_for_owner_name)
async def process_changing_owner(message: types.Message, state: FSMContext):
    data = await dp.current_state().get_data()
    room_number = data['room_number']
    previous_owner = message.chat.id
    new_owner = message.text

    keyboard_inline = generate_inline_keyboard(
        {
            "Вернуться назад ◀️": f"room_menu_{room_number}"
        }
    )

    owner: User = await room_db().change_owner(new_owner,
                                               room_number)

    logger.info(f'The owner ({previous_owner}) of room '
                f'"{room_number}" has been changed to "{owner.user_id}"')

    await state.finish()
    if owner:
        await message.answer(
            '"Хо-хо-хо! 🎅\n\n'
            f'Я сменил владельца, теперь это *{owner.username}*',
            reply_markup=keyboard_inline
        )
    else:
        await message.answer(
            'Такой участник не найден.',
            reply_markup=keyboard_inline
        )
