from sqlalchemy import (BigInteger, Boolean, Column, DateTime, ForeignKey,
                        Integer, LargeBinary, String, Table)
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.sql import func

from app.config import load_config
from app.store.encryption import CryptData


class Base(DeclarativeBase):
    pass


rooms_users = Table('rooms_users', Base.metadata,
                    Column('room_id', Integer, ForeignKey('rooms.id', ondelete='CASCADE'), primary_key=True),
                    Column('user_id', BigInteger, ForeignKey('users.user_id', ondelete='CASCADE'), primary_key=True)                    )


class User(Base):
    __tablename__ = 'users'

    user_id = Column(BigInteger, primary_key=True)
    username = Column(String(256), unique=True, nullable=True)
    first_name = Column(String(128), nullable=True)
    last_name = Column(String(128), nullable=True)
    email = Column(String(64), nullable=True)
    encrypted_address = Column(LargeBinary, nullable=True)
    encrypted_number = Column(LargeBinary, nullable=True)
    registered_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    timezone = Column(String(32), nullable=True)
    language = Column(String(3), nullable=True)
    room_owner = relationship("Room", back_populates="owner")
    members = relationship("Room", secondary=rooms_users, back_populates="members")
    wishes_in_room = relationship("WishRoom",
                                  back_populates="user", overlaps="user_wishes")
    user_wishes = relationship("WishRoom", back_populates="user", overlaps="wishes_in_room")
    recipients = relationship("GameResult", foreign_keys='GameResult.recipient_id', back_populates="recipient")
    senders = relationship("GameResult", foreign_keys='GameResult.sender_id', back_populates="sender")

    def get_address(self) -> str | None:
        if self.encrypted_address:
            crypt = CryptData(key=load_config().encryption.key)
            return crypt.decrypt(self.encrypted_address).decode('UTF8')
        return None

    def get_number(self) -> str | None:
        if self.encrypted_number:
            crypt = CryptData(key=load_config().encryption.key)
            return crypt.decrypt(self.encrypted_number).decode('UTF8')
        return None

    def __str__(self):
        return f"User {self.user_id} : {self.username}"


class Room(Base):
    __tablename__ = 'rooms'

    id = Column(Integer, primary_key=True)
    name = Column(String(16), nullable=False)
    number = Column(Integer, unique=True, nullable=False)
    budget = Column(String(16), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_closed = Column(Boolean, default=False)
    started_at = Column(DateTime(timezone=True), nullable=True)
    closed_at = Column(DateTime(timezone=True), nullable=True)
    owner_id = Column(BigInteger, ForeignKey('users.user_id', ondelete='SET NULL'), nullable=True)

    owner = relationship("User", back_populates="room_owner")
    members = relationship("User", secondary=rooms_users, back_populates="members", lazy="selectin")
    wishes = relationship("WishRoom", back_populates="room", cascade="all, delete-orphan")
    results_of_rooms = relationship("GameResult", back_populates="room")

    def __str__(self):
        return f"Room {self.number}: {self.name}"


class WishRoom(Base):
    __tablename__ = 'wishes_rooms'

    room_id = Column(Integer, ForeignKey('rooms.id', ondelete='CASCADE'), primary_key=True)
    user_id = Column(BigInteger, ForeignKey('users.user_id', ondelete='CASCADE'), primary_key=True)
    wish = Column(String(256), nullable=False)

    room = relationship("Room", back_populates="wishes")
    user = relationship("User", back_populates="user_wishes")


class GameResult(Base):
    __tablename__ = 'game_results'

    id = Column(Integer, primary_key=True)
    room_id = Column(Integer, ForeignKey('rooms.id', ondelete='CASCADE'))
    recipient_id = Column(BigInteger, ForeignKey('users.user_id'))
    sender_id = Column(BigInteger, ForeignKey('users.user_id'))
    assigned_at = Column(DateTime(timezone=True), server_default=func.now())

    room = relationship("Room", back_populates="results_of_rooms")
    recipient = relationship("User", foreign_keys=[recipient_id], back_populates="recipients")
    sender = relationship("User", foreign_keys=[sender_id], back_populates="senders")

    def __str__(self):
        return f"Room {self.room_id}: {self.recipient_id} {self.sender_id}"


class UsersMessages(Base):
    __tablename__ = 'users_messages'

    id = Column(Integer, primary_key=True)
    recipient_id = Column(BigInteger, ForeignKey('users.user_id', ondelete='CASCADE'))
    sender_id = Column(BigInteger, ForeignKey('users.user_id', ondelete='CASCADE'))
    room_id = Column(Integer, ForeignKey('rooms.id', ondelete='CASCADE'))
    message = Column(String(), nullable=True)
    sent_at = Column(DateTime(timezone=True), nullable=True)
