import asyncio
import datetime
import logging
import random

from app.bot.messages.forrmatter import message_formatter
from app.bot.messages.send_messages import send_message, broadcaster
from app.bot.messages.users_checker import checking_user_is_active
from app.store.database.queries.game_result import GameResultDB
from app.store.database.queries.rooms import RoomDB
from app.store.database.queries.wishes import WishDB

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


async def creating_active_users_pool(room_number):
    room_members = await RoomDB.get_list_members(room_number)
    row_list_players = [member for member in room_members]
    verified_users_list = []
    
    for player in row_list_players:
        is_active_user = await checking_user_is_active(player.user_id)
        
        if is_active_user:
            wish = await WishDB.get(player.user_id, room_number)
            
            player_information = {
                'player_id': player.user_id,
                'player_address': player.address,
                'player_first_name': player.first_name,
                'player_last_name': player.last_name,
                'player_contact_number': player.contact_number,
                'player_wish': wish.wish
            }
            
            verified_users_list.append(player_information)
        await asyncio.sleep(.05)  # 20 request per second
    
    return verified_users_list

#TODO Необходимо сделать, что бы при отправке проверялось,
# что участников больше 3х человек
async def send_result_of_game(room_number) -> None:
    verified_users = await creating_active_users_pool(room_number)
    random.shuffle(verified_users)
    persons = [Person(user) for user in verified_users]
    persons[-1].set_sender(persons[0])
    prepared_users_list = []
    
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
        wish_to_send = (
            person.to_send.player['player_wish']
            if person.to_send.player['player_wish'] else ''
        )
        
        await GameResultDB.insert(
            room_id=room_number,
            recipient_id=recipient_id,
            sender_id=sender_id,
        )
        
        await RoomDB.update(
            room_number=room_number,
            is_closed=True,
            closed_at=datetime.datetime.now()
        )
        
        message_text = message_formatter(
            sender_name=sender_name,
            receiver_first_name=receiver_first_name,
            receiver_last_name=receiver_last_name,
            address=address_to_send,
            phone=phone_to_send,
            wish=wish_to_send
        )
        
        prepared_users_list.append(
            {
               'user_id': person.player['player_id'],
                'text': message_text
                
            }
        )

    await broadcaster(prepared_users_list)
