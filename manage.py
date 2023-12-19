import argparse
import logging
import requests

from app.config import load_config

logger = logging.getLogger(__name__)


def set_admin(username):
    # TODO дописать изменение роли
    pass
    
def register_webhook():
    url = (
        f'https://api.telegram.org/bot{load_config().bot.token}/'
        f'setWebhook?url={load_config().web.site_url}/bot/')
    
    response = requests.get(url)
    data = response.json()
    print(f'Result: {data.get("result")}')
    print(f'Result: {data.get("description")}')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Secret Santa Bot Configuration.')
    subparsers = parser.add_subparsers(title='Allowed Commands:',
                                       dest='command')
    set_admin_parser = subparsers.add_parser('set_admin',
                                          help='Set administrator rights to user.')
    set_admin_parser.add_argument('telegram_id',
                                  help='Administrator TelegramID')

    register_webhook_parser = subparsers.add_parser('register_webhook',
                                          help='Set telegram webhook url.')

    args = parser.parse_args()

    if args.command == 'set_admin':
        set_admin(args.telegram_id)
    if args.command == 'register_webhook':
        register_webhook()
    else:
        print("Incorrect command.")
