import os
from dataclasses import dataclass

from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(dotenv_path)


@dataclass
class BotConfig:
    token: str


@dataclass
class DataBaseConfig:
    database_name: str
    user: str
    password: str
    port: str


@dataclass
class AppConfig:
    bot: BotConfig
    database: DataBaseConfig


config = AppConfig(
    bot=BotConfig(
        token=os.getenv("TELEGRAM_TOKEN"),
    ),
    database=DataBaseConfig(
        database_name=os.getenv("DATABASE_NAME"),
        user=os.getenv("DATABASE_USER"),
        password=os.getenv("DATABASE_PASSWORD"),
        port=os.getenv("DATABASE_PORT"),
    ),
)
