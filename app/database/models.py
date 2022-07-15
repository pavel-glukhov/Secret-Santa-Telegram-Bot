from datetime import datetime

from sqlalchemy import Column, Integer, String, ForeignKey, BigInteger, \
    DateTime, Boolean
from sqlalchemy.orm import relationship
from app.database.config import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, nullable=False)
    username = Column(String(56), nullable=False)
    first_name = Column(String(56), nullable=True)
    last_name = Column(String(56), nullable=True)
    email = Column(String(56), nullable=True)
    address = Column(String(), nullable=True)
    contact_number = Column(String(18), nullable=True)
    registered_at = Column(DateTime, nullable=False, default=datetime.now())
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    room = relationship('Room', secondary='rooms_users', backref='users')

    def __repr__(self):
        return f'username:{self.username} user_id:{self.telegram_id}'


class Room(Base):
    __tablename__ = 'rooms'

    id = Column(Integer, primary_key=True)
    name = Column(String(12), nullable=False)
    number = Column(Integer(), nullable=False, unique=True)
    owner_id = Column(Integer, ForeignKey('users.id'))
    owner = relationship('User', backref='owner_of_room')
    members = relationship('User', secondary='rooms_users', backref='rooms')
    budget = Column(String(12), nullable=False)
    created_ad = Column(DateTime, default=datetime.now())
    is_started = Column(Boolean, default=False)
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f'room name:{self.name} number:{self.number}'


class RoomUser(Base):
    __tablename__ = "rooms_users"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    room_id = Column(Integer, ForeignKey('rooms.id'))


class Note(Base):
    __tablename__ = 'notes'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User', backref='member')
    room_id = Column(Integer, ForeignKey('rooms.id'))
    room = relationship('Room', backref='room')
    note = Column(String(256), nullable=True)


class GameResult(Base):
    __tablename__ = "games_results"

    id = Column(Integer, primary_key=True)
    room_id = Column(Integer, ForeignKey('rooms.id'))
    room = relationship('Room', backref='game_result')
    recipient_id = Column(Integer, ForeignKey('users.id'))
    sender_id = Column(Integer, ForeignKey('users.id'))
    assigned_at = Column(DateTime)
