from app.bot.handlers.communication import (message_to_recipient,
                                            message_to_sender)
from app.bot.handlers.game import start_game_general_menu
from app.bot.handlers.profiles import (change_address, change_name,
                                       change_number, delete_information,
                                       profile_general_menu)
from app.bot.handlers.rooms import (activate, change_budget, change_owner,
                                    config_room, create_new_room, delete_room,
                                    members, rooms_general_menu, subscribe,
                                    unsubscribe, update_room)
from app.bot.handlers.start import about, language, start_handler
from app.bot.handlers.time_zones import change_timezone_general_menu
from app.bot.handlers.wishes import wishes_general_menu


def register_routers(dp) -> None:
    # start
    dp.include_router(start_handler.router)
    dp.include_router(language.router)
    dp.include_router(about.router)
    # profile
    dp.include_router(profile_general_menu.router)
    dp.include_router(change_name.router)
    dp.include_router(change_number.router)
    dp.include_router(change_address.router)
    dp.include_router(delete_information.router)
    dp.include_router(change_timezone_general_menu.router)
    # start game
    dp.include_router(start_game_general_menu.router)
    # wishes
    dp.include_router(wishes_general_menu.router)
    # communication
    dp.include_router(message_to_sender.router)
    dp.include_router(message_to_recipient.router)
    # rooms
    dp.include_router(activate.router)
    dp.include_router(change_budget.router)
    dp.include_router(change_owner.router)
    dp.include_router(config_room.router)
    dp.include_router(create_new_room.router)
    dp.include_router(delete_room.router)
    dp.include_router(members.router)
    dp.include_router(rooms_general_menu.router)
    dp.include_router(subscribe.router)
    dp.include_router(unsubscribe.router)
    dp.include_router(update_room.router)
