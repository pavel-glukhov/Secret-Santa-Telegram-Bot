import asyncio
import logging
import random
from aiogram.utils import exceptions

from app import bot
from app.database import room_db, wish_db
from app.utils.formatters import message_for_secret_santa

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


async def get_users(room_number) -> list:
    """
    Return users list
    """

    members = await room_db().get_list_members_of_room(room_number)
    room_members = [member.user_id for member in members]
    return room_members


async def test(room_number):
    list_addresses = []
    players = await get_users(room_number)

    if len(players) > 0:
        for player in players:
            wish = await wish_db().get_wishes(
                user_id=player.user_id,
                room_id=room_number
            )
            address_diction = {
                'user_id': player.user_id,
                'address': player.address,
                'recipient_name': f'{player.first_name} {player.last_name}',
                'contact_number': player.contact_number,
                'wish': wish.wish
            }

            list_addresses.append(address_diction)

    else:
        logger.info('list players is empty')
        return False

    random.shuffle(list_addresses)

    persons = [Person(person) for person in list_addresses]
    persons[-1].set_sender(persons[0])

    for ind in range(len(persons) - 1):
        persons[ind].set_sender(persons[ind + 1])

    for person in persons:
        name_to_send = person.to_send.player['recipient_name']
        address_to_send = person.to_send.player['address']
        phone_to_send = person.to_send.player['contact_number']
        comment_to_send = person.to_send.player['comment'] if \
            person.to_send.player['comment'] else ''
        print(f'{person.player["recipient_name"]} {name_to_send}')

        message_text = message_for_secret_santa(
            santa_name=person.player["recipient_name"],
            receipt_name=name_to_send,
            receipt_address=address_to_send,
            receipt_number=phone_to_send,
            receipt_wish=comment_to_send

        )


async def send_message(user_id: int,
                       text: str,
                       disable_notification: bool = False) -> bool:
    """
    Safe messages sender
    :param user_id:
    :param text:
    :param disable_notification:
    :return:
    """
    try:
        await bot.send_message(user_id, text,
                               disable_notification=disable_notification)
    except exceptions.BotBlocked:
        logger.error(f"Target [ID:{user_id}]: blocked by user")
    except exceptions.ChatNotFound:
        logger.error(f"Target [ID:{user_id}]: invalid user ID")
    except exceptions.RetryAfter as e:
        logger.error(
            f"Target [ID:{user_id}]: Flood limit is exceeded."
            f" Sleep {e.timeout} seconds.")
        await asyncio.sleep(e.timeout)
        return await send_message(user_id, text)  # Recursive call
    except exceptions.UserDeactivated:
        logger.error(f"Target [ID:{user_id}]: user is deactivated")
    except exceptions.TelegramAPIError:
        logger.exception(f"Target [ID:{user_id}]: failed")
    else:
        logger.info(f"Target [ID:{user_id}]: success")
        return True
    return False


async def broadcaster(room_number, text) -> int:
    """
    broadcaster
    :return: Count of messages
    """
    count = 0
    try:
        for user_id in await get_users(room_number):
            if await send_message(user_id, text):
                count += 1
            await asyncio.sleep(
                .05)  # 20 messages per second (Limit: 30 messages per second)
    finally:
        logger.info(f"{count} messages successful sent.")

    return count
