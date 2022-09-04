import os
from dataclasses import dataclass
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(dotenv_path)

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

config = AppConfig(
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
)