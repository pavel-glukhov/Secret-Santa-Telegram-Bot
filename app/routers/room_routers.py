from aiogram import Dispatcher
from app.handlers.rooms.common import my_room
from app.handlers.rooms.create_room import (CreateRoom, create_room,
                                            process_budget, process_name,
                                            process_wishes)
from app.handlers.rooms.delete_room import (DeleteRoom,
                                            completed_process_delete_room,
                                            process_delete_room_invalid)
from app.handlers.rooms.subscribe_room import (JoinRoom, join_room,
                                               process_room_number,
                                               process_room_wishes)
from app.handlers.rooms.update_room import (ChangeRoomName,
                                            update_room_name_get_value)
from app.handlers.rooms.validators import (process_join_room_invalid_text_type,
                                           room_name_invalid)
from app.keyborads.constants import MAIN_REPLY_BUTTONS


def setup_room_handlers(dp: Dispatcher):
    # common room handlers
    dp.register_message_handler(
        my_room,
        lambda message: message.text.startswith(
            "Ваша комната:")
    )

    # create room handlers
    dp.register_message_handler(
        create_room,
        lambda
            message: message.text == MAIN_REPLY_BUTTONS['create_room'],
        state=None
    )
    dp.register_message_handler(
        room_name_invalid,
        lambda message: len(message.text) > 12,
        state=CreateRoom.waiting_for_room_name
    )
    dp.register_message_handler(
        process_name,
        state=CreateRoom.waiting_for_room_name
    )
    dp.register_message_handler(
        process_budget,
        state=CreateRoom.waiting_for_room_budget
    )
    dp.register_message_handler(
        process_wishes,
        state=CreateRoom.waiting_for_room_wishes
    )

    # Join room
    dp.register_message_handler(join_room, lambda
        message: message.text == MAIN_REPLY_BUTTONS['join_room'],
                                state=None)
    dp.register_message_handler(process_join_room_invalid_text_type,
                                lambda message: not message.text.isdigit(),
                                state=JoinRoom.waiting_for_room_number)
    dp.register_message_handler(process_room_number,
                                state=JoinRoom.waiting_for_room_number)
    dp.register_message_handler(process_room_wishes,
                                state=JoinRoom.waiting_for_wishes)

    # delete rooms
    dp.register_message_handler(process_delete_room_invalid,
                                lambda message:
                                message.text.lower() != 'подтверждаю',
                                state=DeleteRoom.waiting_conformation)

    dp.register_message_handler(completed_process_delete_room,
                                state=DeleteRoom.waiting_conformation)

    # Update rooms
    dp.register_message_handler(update_room_name_get_value,
                                state=ChangeRoomName.waiting_for_room_name)

    dp.register_message_handler(room_name_invalid,
                                lambda message: len(message.text) > 12,
                                state=ChangeRoomName.waiting_for_room_name)
