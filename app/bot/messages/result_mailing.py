import asyncio
import datetime
import logging
import random

from app.bot.keyborads.common import generate_inline_keyboard
from app.bot.languages import TranslationMainSchema, language_return_dataclass
from app.bot.messages.forrmatter import message_formatter
from app.bot.messages.send_messages import broadcaster, send_message
from app.bot.messages.users_checker import checking_user_is_active
from app.store.database.queries.game_result import GameResultRepo
from app.store.database.queries.rooms import RoomRepo
from app.store.database.queries.wishes import WishRepo
from app.store.database.sessions import get_session
from app.store.redis import get_redis_client
from app.store.scheduler.operations import remove_task

logger = logging.getLogger(__name__)


class Person:
    """
    Circular list for sending a random list of addresses
    """
    
    def __init__(self, player: dict):
        self.player = player
        self.to_send = None
    
    def set_sender(self, player_to_send):
        self.to_send = player_to_send


async def creating_active_users_pool(
        room_number, session, radis_client) -> list:
    room_members = await RoomRepo(session).get_list_members(room_number)
    row_list_players = [member for member in room_members]
    verified_users_list = []
    
    for player in row_list_players:
        is_active_user = await checking_user_is_active(player.user_id, session)
        if is_active_user:
            wish = await WishRepo(session).get(player.user_id, room_number)
            player_information = {
                'player_id': player.user_id,
                'player_name': player.first_name,
                'player_address': player.get_address(),
                'player_first_name': player.first_name,
                'player_last_name': player.last_name,
                'player_contact_number': player.get_number(),
                'player_wish': wish if wish is not None else None,
                'player_language': await language_return_dataclass(radis_client, player.language)
            }
            
            verified_users_list.append(player_information)
        await asyncio.sleep(.05)  # 20 request per second
    
    return verified_users_list


async def send_result_of_game(room_number,
                              semaphore) -> None:
    session_generator = get_session()
    session = next(session_generator)
    redis_client = get_redis_client()

    async with semaphore:
        verified_users = await creating_active_users_pool(room_number, session, redis_client)
        
        if not _check_sending_capability(verified_users):
            return await _insufficient_number_players(room_number, session)
        
        data = await _prepare_data_to_send(verified_users, room_number, session)
        await RoomRepo(session).update(room_number,
                                       is_closed=True,
                                       closed_at=datetime.datetime.now())
        
        return await broadcaster(data)


async def _prepare_data_to_send(
        verified_users: list, room_number: int, session) -> list:
    random.shuffle(verified_users)
    persons = [Person(user) for user in verified_users]
    persons[-1].set_sender(persons[0])
    sending_data = []
    
    for index in range(len(persons) - 1):
        persons[index].set_sender(persons[index + 1])
    
    for person in persons:
        sender_id = person.player['player_id']
        sender_name = person.player["player_name"]
        recipient_id = person.to_send.player['player_id']
        receiver_first_name = person.to_send.player["player_first_name"]
        receiver_last_name = person.to_send.player["player_last_name"]
        address_to_send = person.to_send.player['player_address']
        phone_to_send = person.to_send.player['player_contact_number']
        player_language = person.player['player_language']
        
        wish_to_send = (
            person.to_send.player['player_wish']
            if person.to_send.player['player_wish'] else ''
        )
        await GameResultRepo(session).insert(room_number,
                                             recipient_id,
                                             sender_id)
        
        message_text = message_formatter(sender_name,
                                         receiver_first_name,
                                         receiver_last_name,
                                         address_to_send,
                                         phone_to_send,
                                         wish_to_send,
                                         player_language)
        sending_data.append(
            {
                'user_id': person.player['player_id'],
                'text': message_text,
                'player_language': player_language
            }
        )
    return sending_data


def _check_sending_capability(verified_users):
    count_verified_users = len(verified_users)
    if count_verified_users < 3:
        return False
    return True


async def _insufficient_number_players(room_number: int,
                                       session) -> None:

    room = await RoomRepo(session).get(room_number)
    owner = room.owner
    app_language = await language_return_dataclass(get_redis_client(), owner.language)
    
    keyboard_inline = {
        app_language.buttons.menu: "start_menu",
    }
    await RoomRepo(session).update(room_number,
                                   is_closed=True,
                                   closed_at=datetime.datetime.now())
    
    remove_task(room_number)
    message_text = app_language.result_mailing.message_text.format(
        room_name=room.name
    )
    
    await send_message(
        user_id=owner.user_id,
        text=message_text,
        reply_markup=generate_inline_keyboard(keyboard_inline)
    )
    
    logger.info(f'Insufficient number of players '
                f'for the room [{room_number}]. The task was removed.')
