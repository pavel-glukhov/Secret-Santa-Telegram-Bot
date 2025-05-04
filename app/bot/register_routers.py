from app.bot.handlers.communication import (message_to_recipient,
                                            message_to_sender)
from app.bot.handlers.game import startgame_main
from app.bot.handlers.profiles import (change_address, change_name,
                                       change_number, delete_information,
                                       profile_general_menu)
from app.bot.handlers.rooms import (activate, change_budget, change_owner,
                                    settings_menu, create_new_room, delete_room,
                                    members, rooms_general_menu, subscribe,
                                    unsubscribe, update_room)
from app.bot.handlers.start import about, language, start_handler
from app.bot.handlers.time_zones import change_timezone_general_menu
from app.bot.handlers.wishes import wishes_general_menu


def register_start_handlers(dp) -> None:
    dp.include_router(start_handler.router)
    dp.include_router(language.router)
    dp.include_router(about.router)


def register_profile_handlers(dp) -> None:
    dp.include_router(profile_general_menu.router)
    dp.include_router(change_name.router)
    dp.include_router(change_number.router)
    dp.include_router(change_address.router)
    dp.include_router(delete_information.router)
    dp.include_router(change_timezone_general_menu.router)


def register_game_handlers(dp) -> None:
    dp.include_router(startgame_main.router)


def register_wishes_handlers(dp) -> None:
    dp.include_router(wishes_general_menu.router)


def register_communication_handlers(dp) -> None:
    dp.include_router(message_to_sender.router)
    dp.include_router(message_to_recipient.router)


def register_room_handlers(dp) -> None:
    dp.include_router(activate.router)
    dp.include_router(change_budget.router)
    dp.include_router(change_owner.router)
    dp.include_router(settings_menu.router)
    dp.include_router(create_new_room.router)
    dp.include_router(delete_room.router)
    dp.include_router(members.router)
    dp.include_router(rooms_general_menu.router)
    dp.include_router(subscribe.router)
    dp.include_router(unsubscribe.router)
    dp.include_router(update_room.router)


def register_routers(dp) -> None:
    register_start_handlers(dp)
    register_profile_handlers(dp)
    register_game_handlers(dp)
    register_wishes_handlers(dp)
    register_communication_handlers(dp)
    register_room_handlers(dp)
