import logging.config
import os
from dataclasses import dataclass

import yaml
from dotenv import load_dotenv
from starlette.templating import Jinja2Templates

root_path = os.path.dirname(os.path.dirname(__file__))
dotenv_path = os.path.join(root_path, '.env')
templates = Jinja2Templates(directory=os.path.join(root_path, "templates"))
load_dotenv(dotenv_path)


@dataclass()
class JWTSettings:
    authjwt_secret_key: str


@dataclass()
class WebSettings:
    jwt_settings: JWTSettings
    site_url: str


@dataclass
class LoggingConfig:
    log_path: str
    log_file: str
    config_file: str


@dataclass
class RoomConfig:
    room_number_length: int


@dataclass
class BotConfig:
    token: str
    telegram_login: str


@dataclass
class DataBaseConfig:
    name: str
    user: str
    password: str
    host: str
    port: str


@dataclass
class RedisConfig:
    db: str
    host: str
    port: str
    password: str


@dataclass
class AppConfig:
    bot: BotConfig
    web: WebSettings
    db: DataBaseConfig
    redis: RedisConfig
    room: RoomConfig
    log: LoggingConfig


def load_config():
    """
    Main configuration of application
    """
    return AppConfig(
        bot=BotConfig(
            token=os.getenv('TELEGRAM_TOKEN'),
            telegram_login=os.getenv('TELEGRAM_LOGIN'),
        ),
        web=WebSettings(
            jwt_settings=JWTSettings(
                authjwt_secret_key=os.getenv('AUTH_JWT_SECRET_KEY')
            ),
            site_url=os.getenv('SITE_URL'),
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
            room_number_length=6
        ),
        log=LoggingConfig(
            log_path=os.path.join(root_path, 'logs'),
            log_file='logs.log',
            config_file='logging.yaml'
        ),
    
    )


def webhook_settings(config) -> dict:
    webhook_path = f"/bot/{config().bot.token}"
    webhook_url = config().web.site_url + webhook_path
    return {
        'webhook_path': webhook_path,
        'webhook_url': webhook_url
    }


def setup_logging() -> None:
    config = load_config()
    configuration_file = os.path.join(root_path, config.log.config_file)
    
    with open(configuration_file, 'r') as stream:
        logging_cfg = yaml.load(stream, Loader=yaml.FullLoader)
    
    logging_cfg['handlers'][
        'timed_rotating_handler']['filename'] = os.path.join(
        config.log.log_path,
        config.log.log_file
    )
    logging.config.dictConfig(logging_cfg)