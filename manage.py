import argparse
import asyncio
import logging

import requests

from app.config import load_config
from app.store.database import close_db, init_db
from app.store.queries.users import UserRepo

logger = logging.getLogger(__name__)


async def update_user_permissions(telegram_user_id, is_superuser: bool):
    await init_db()
    user = await UserRepo().get_user_or_none(int(telegram_user_id))
    if user:
        await UserRepo().update_user(int(telegram_user_id),
                                     is_superuser=is_superuser)
    await close_db()
    return True if user else False


def set_superuser(telegram_user_id):
    result = asyncio.run(update_user_permissions(telegram_user_id, True))
    if result:
        return print(f'Superuser rights have been set.')
    return print(f'Check entered telegram ID')


def remove_superuser(telegram_user_id):
    result = asyncio.run(update_user_permissions(telegram_user_id, False))
    if result:
        return print(f'Superuser rights have been removed.')
    return print(f'Check entered telegram ID')


def register_webhook():
    url = (
        f'https://api.telegram.org/bot{load_config().bot.token}/'
        f'setWebhook?url={load_config().web.domain_name}/bot/')
    
    response = requests.get(url)
    data = response.json()
    print(f'Result: {data.get("result")}')
    print(f'Result: {data.get("description")}')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Secret Santa Bot Configuration.')
    subparsers = parser.add_subparsers(title='Allowed Commands:',
                                       dest='command')
    set_superuser_parser = subparsers.add_parser(
        'set_superuser',
        help='Set administrator rights to user.')
    set_superuser_parser.add_argument('telegram_id', type=int,
                                      help='Administrator TelegramID')
    
    remove_superuser_parser = subparsers.add_parser(
        'remove_superuser',
        help='Remove administrator rights from user.')
    remove_superuser_parser.add_argument('telegram_id', type=int,
                                         help='Administrator TelegramID')
    
    register_webhook_parser = subparsers.add_parser(
        'register_webhook',
        help='Set telegram webhook url.')
    
    args = parser.parse_args()
    
    if args.command == 'set_superuser':
        set_superuser(args.telegram_id)
    elif args.command == 'remove_superuser':
        remove_superuser(args.telegram_id)
    elif args.command == 'register_webhook':
        register_webhook()
    else:
        print("Incorrect command.")
