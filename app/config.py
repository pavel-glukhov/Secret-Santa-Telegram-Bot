import os
from dataclasses import dataclass

from dotenv import load_dotenv

root_path = os.path.dirname(os.path.dirname(__file__))
dotenv_path = os.path.join(root_path, '.env')

load_dotenv(dotenv_path)


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
    db: DataBaseConfig
    redis: RedisConfig
    room: RoomConfig
    log: LoggingConfig


def app_config():
    """
    Main configuration of application
    """
    return AppConfig(
        bot=BotConfig(
            token=os.getenv("TELEGRAM_TOKEN"),
        ),
        db=DataBaseConfig(
            name=os.getenv("DATABASE_NAME"),
            user=os.getenv("DATABASE_USER"),
            password=os.getenv("DATABASE_PASSWORD"),
            port=os.getenv("DATABASE_PORT"),
            host=os.getenv("DATABASE_HOST"),
        ),
        redis=RedisConfig(
            db=os.getenv("REDIS_DB"),
            host=os.getenv("REDIS_HOST"),
            port=os.getenv("REDIS_PORT"),
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

