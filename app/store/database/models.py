from tortoise import fields
from tortoise.models import Model

from app.config import load_config
from app.store.encryption import CryptData


class User(Model):
    user_id = fields.BigIntField(pk=True)
    username = fields.CharField(max_length=256, unique=True, null=True)
    first_name = fields.CharField(max_length=128, null=True)
    last_name = fields.CharField(max_length=128, null=True)
    email = fields.CharField(max_length=64, null=True)
    encrypted_address = fields.BinaryField(null=True)
    encrypted_number = fields.BinaryField(null=True)
    registered_at = fields.DatetimeField(auto_now_add=True)
    is_active = fields.BooleanField(default=True)
    is_superuser = fields.BooleanField(default=False)
    timezone = fields.CharField(max_length=32, null=True)
    
    class Meta:
        table = "users"
    
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


class Room(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=16, null=False)
    number = fields.IntField(null=False, unique=True)
    budget = fields.CharField(max_length=16, null=False)
    created_at = fields.DatetimeField(auto_now_add=True)
    is_closed = fields.BooleanField(default=False)
    started_at = fields.DatetimeField(null=True)
    closed_at = fields.DatetimeField(null=True)
    owner = fields.ForeignKeyField('models.User',
                                   related_name='room_owner')
    members = fields.ManyToManyField('models.User',
                                     related_name='members',
                                     through='rooms_users',
                                     on_delete='CASCADE')
    wishes = fields.ManyToManyField('models.User',
                                    through='wishes_rooms',
                                    related_name='wishes_in_room',
                                    on_delete='CASCADE')
    
    class Meta:
        table = "rooms"
    
    def __str__(self):
        return f"Room {self.number}: {self.name}"


class WishRoom(Model):
    room = fields.ForeignKeyField('models.Room', related_name='room_wishes')
    user = fields.ForeignKeyField('models.User', related_name='user_wishes')
    wish = fields.CharField(max_length=256, null=False)
    
    class Meta:
        table = "wishes_rooms"


class GameResult(Model):
    id = fields.IntField(pk=True)
    room = fields.ForeignKeyField('models.Room',
                                  related_name='results_of_rooms')
    recipient = fields.ForeignKeyField('models.User',
                                       related_name='recipients')
    sender = fields.ForeignKeyField('models.User',
                                    related_name='senders')
    assigned_at = fields.DatetimeField(auto_now_add=True)
    
    class Meta:
        table = "game_results"
    
    def __str__(self):
        return f"Room {self.room}: {self.recipient} {self.sender}"
