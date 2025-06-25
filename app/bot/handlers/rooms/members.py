import logging

from aiogram import F, Router, types
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyborads.common import generate_inline_keyboard
from app.bot.languages.schemes import TranslationMainSchema
from app.core.database.repo.rooms import RoomRepo

logger = logging.getLogger(__name__)

router = Router()


@router.callback_query(F.data.startswith('room_member-list'))
async def members_list(callback: types.CallbackQuery,
                       session: AsyncSession,
                       lang: TranslationMainSchema,
                       room_number: int):
    return_back_button = lang.buttons.return_back_button
    keyboard_inline = generate_inline_keyboard(
        {
            return_back_button: f'room_menu_{room_number}'
        }
    )
    room = await RoomRepo(session).get(room_number)
    members = room.members

    message_text = lang.messages.rooms_menu.members.menu_msg.format(
        room_name=room.name,
        room_number=room_number,
        member_string=_generate_user_name_list(members)
    )

    await callback.message.edit_text(
        text=message_text,
        reply_markup=keyboard_inline,
    )


def _generate_user_name_list(members) -> str:
    member_string = ''
    for number, member in enumerate(members, start=1):
        if member.first_name:
            if member.username and member.last_name:
                user_name = (f'@{member.username} - '
                             f'{member.first_name} {member.last_name}')
            elif member.username and not member.last_name:
                user_name = f'@{member.username} - {member.first_name}'
            elif not member.username and member.last_name:
                user_name = f'{member.first_name} {member.last_name}'

            else:
                user_name = member.first_name
        else:
            user_name = None

        member_string += (
            f'{number}) {user_name}\n')
    return member_string
