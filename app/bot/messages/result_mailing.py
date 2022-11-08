import asyncio
import datetime
import logging
import random

from app.bot.messages.forrmatter import format_santa_message
from app.bot.messages.send_messages import send_message
from app.bot.messages.users_checker import is_active_user_chat
from app.store.database import game_result_db, room_db, wish_db

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


# TODO loging
async def creating_users_pool(room_number):
    room_members = await room_db().get_list_members(room_number)
    row_list_players = [member for member in room_members]
    verified_list_players = []
    
    for player in row_list_players:
        is_active_player_char = await is_active_user_chat(player.user_id)
        
        if is_active_player_char:
            wish = await wish_db().get(player.user_id, room_number)
            
            player_information = {
                'player_id': player.user_id,
                'player_address': player.address,
                'player_first_name': player.first_name,
                'player_last_name': player.last_name,
                'player_contact_number': player.contact_number,
                'player_wish': wish.wish
            }
            
            verified_list_players.append(player_information)
        await asyncio.sleep(.05)  # 20 request per second (Limit: 30 messages per second)
    
    return verified_list_players


# TODO loging
# TODO обновить GameResult таблицу
async def send_result_of_game(room_number) -> None:
    list_players = await creating_users_pool(room_number)
    random.shuffle(list_players)
    persons = [Person(person) for person in list_players]
    persons[-1].set_sender(persons[0])
    
    for ind in range(len(persons) - 1):
        persons[ind].set_sender(persons[ind + 1])
    
    for p in persons:
        sender_id = p.player['player_id']
        sender_name = p.player["player_name"]
        recipient_id = p.to_send.player['player_id']
        receiver_first_name = p.to_send.player["player_first_name"]
        receiver_last_name = p.to_send.player["player_last_name"]
        address_to_send = p.to_send.player['player_address']
        phone_to_send = p.to_send.player['player_contact_number']
        wish_to_send = p.to_send.player['player_wish'] if p.to_send.player['player_wish'] else ''
        
        await game_result_db().insert(
            room_id=room_number,
            recipient_id=recipient_id,
            sender_id=sender_id,
        )
        
        message_text = format_santa_message(
            sender_name=sender_name,
            receiver_first_name=receiver_first_name,
            receiver_last_name=receiver_last_name,
            address=address_to_send,
            phone=phone_to_send,
            wish=wish_to_send
        )
        
        await send_message(user_id=p.player['player_id'], text=message_text)
    
    await room_db().update(room_number=room_number,
                           is_closed=True,
                           closed_at=datetime.datetime.now()
                           )
