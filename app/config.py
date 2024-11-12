import logging.config
import os
from dataclasses import dataclass
from functools import lru_cache

import yaml
from dotenv import load_dotenv

ROOT_PATH = os.path.dirname(os.path.dirname(__file__))
dotenv_path = os.path.join(ROOT_PATH, '.env')
load_dotenv(dotenv_path)


@dataclass()
class JWTSettings:
    authjwt_secret_key: str


@dataclass()
class WebSettings:
    jwt_settings: JWTSettings
    domain_name: str


@dataclass
class LoggingConfig:
    log_path: str
    log_file: str
    config_file: str


@dataclass
class RoomConfig:
    room_number_length: int
    user_rooms_count: int


@dataclass
class BotConfig:
    token: str
    telegram_login: str
    language_folder: str


@dataclass
class DataBaseConfig:
    name: str
    user: str
    password: str
    host: str
    port: str
    
    @property
    def postgres_url(self):
        return (f'postgresql://'
                f'{self.user}:'
                f'{self.password}'
                f'@{self.host}/'
                f'{self.name}')


@dataclass
class RedisConfig:
    db: str
    host: str
    port: str
    password: str


@dataclass
class Encryption:
    key: str


@dataclass
class AppConfig:
    bot: BotConfig
    web: WebSettings
    db: DataBaseConfig
    redis: RedisConfig
    room: RoomConfig
    log: LoggingConfig
    encryption: Encryption
    support_account: str


@lru_cache
def load_config() -> AppConfig:
    """
    Main configuration of application
    """
    return AppConfig(
        bot=BotConfig(
            token=os.getenv('TELEGRAM_TOKEN'),
            telegram_login=os.getenv('TELEGRAM_LOGIN'),
            language_folder=os.path.join(ROOT_PATH, 'app\\bot\\languages')
        ),
        web=WebSettings(
            jwt_settings=JWTSettings(
                authjwt_secret_key=os.getenv('AUTH_JWT_SECRET_KEY')
            ),
            domain_name=os.getenv('DOMAIN_NAME'),
        ),
        db=DataBaseConfig(
            name=os.getenv('DATABASE_NAME'),
            user=os.getenv('DATABASE_USER'),
            password=os.getenv('DATABASE_PASSWORD'),
            port=os.getenv('DATABASE_PORT'),
            host=os.getenv('DATABASE_HOST'),
        ),
        redis=RedisConfig(
            db=os.getenv('REDIS_DB'),
            host=os.getenv('REDIS_HOST'),
            port=os.getenv('REDIS_PORT'),
            password=os.getenv("REDIS_PASSWORD"),
        ),
        room=RoomConfig(
            room_number_length=int(os.getenv('ROOM_NUBER_LENGTH')),
            user_rooms_count=int(os.getenv('USER_ROOMS_LIMIT'))
        ),
        log=LoggingConfig(
            log_path=os.path.join(ROOT_PATH, 'logs'),
            log_file='logs.log',
            config_file='logging.yaml'
        ),
        encryption=Encryption(
            key=os.getenv('ENCRYPT_SECRET_KEY')
        ),
        support_account=os.getenv('SUPPORT_ACCOUNT')
    
    )


def webhook_settings(config) -> dict:
    webhook_path = f"/bot/{config().bot.token}"
    webhook_url = 'https://' + config().web.domain_name + webhook_path
    return {
        'webhook_path': webhook_path,
        'webhook_url': webhook_url
    }


def setup_logging() -> None:
    config = load_config()
    configuration_file = os.path.join(ROOT_PATH, config.log.config_file)

    if not os.path.exists(config.log.log_path):
        os.makedirs(config.log.log_path)

    with open(configuration_file, 'r') as stream:
        logging_cfg = yaml.load(stream, Loader=yaml.FullLoader)
    
    logging_cfg['handlers'][
        'timed_rotating_handler']['filename'] = os.path.join(
        config.log.log_path,
        config.log.log_file
    )
    logging.config.dictConfig(logging_cfg)
