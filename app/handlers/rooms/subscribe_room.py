from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode

from app import dispatcher as dp
from app import room_db
from app.keyborads.common import create_common_keyboards


class JoinRoom(StatesGroup):
    waiting_for_room_number = State()
    waiting_for_wishes = State()



async def join_room(message: types.Message):
    await JoinRoom.waiting_for_room_number.set()
    await message.answer(
        '"Хо-хо-хо! 🎅\n\n'
        'Введи номер комнаты в которую ты хочешь зайти.\n\n'
        'Что бы отменить процесс, введите в чате *отмена*',
        parse_mode=ParseMode.MARKDOWN,
    )


# TODO добавить выбор пожелания
async def process_join_room_invalid_text_type(message: types.Message):
    return await message.reply(
        text='Номер комнаты может содержать только цифры, '
             'попробуйте снова.\n'
             'Что бы отменить процесс, введите в чате *отмена*',
        parse_mode=ParseMode.MARKDOWN, )



async def process_room_number(message: types.Message, state: FSMContext):
    user_id = message.chat.id

    async with state.proxy() as data:
        data['room_number'] = message.text

    room_number = message.text

    is_exists = await room_db().is_exists(room_number=room_number)
    if not is_exists:
        await message.answer(
            'Введенной комнаты не существует.',
            parse_mode=ParseMode.MARKDOWN,
        )
    else:
        is_member = await room_db().is_member(user_id=user_id,
                                             room_number=room_number)

        if is_member:
            keyboard = await create_common_keyboards(message)
            await message.answer(
                'Вы уже состоите в этой комнате.',
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboard
            )
            await state.finish()

        else:
            await JoinRoom.next()
            await message.answer(
                'А теперь напишите свои пожелания к подарку. '
                'Возможно у тебя есть хобби и '
                'ты хочешь получить что-то особое?\n'
                'Ваши комментарии помогут Тайному Санте '
                'выбрать для вас подарок.\n\n'
                'Что бы отменить процесс, введите в чате *отмена*',
                parse_mode=ParseMode.MARKDOWN
            )


# TODO добавить создание желания
async def joined_room(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['room_number'] = message.text

        user_id = message.chat.id
        wishes = message.text
        await room_db().add_member(user_id=user_id,
                                  room_number=data['room_number'])

        keyboard = await create_common_keyboards(message)
        await message.answer(
            '"Хо-хо-хо! 🎅\n\n'
            'Теперь ты можешь играть с своими друзьями.\n'
            'Следи за анонсами владельца комнаты.\n\n'
            'Желаю хорошей игры! 😋',
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=keyboard
        )

        await state.finish()
