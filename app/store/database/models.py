from tortoise import fields
from tortoise.models import Model


class User(Model):
    user_id = fields.IntField(pk=True)
    username = fields.CharField(max_length=256, unique=True, null=True)
    first_name = fields.CharField(max_length=128, null=True)
    last_name = fields.CharField(max_length=128, null=True)
    email = fields.CharField(max_length=64, null=True)
    address = fields.CharField(max_length=150, null=True)
    contact_number = fields.CharField(max_length=18, null=True)
    registered_at = fields.DatetimeField(auto_now_add=True)
    is_active = fields.BooleanField(default=True)
    is_superuser = fields.BooleanField(default=False)

    class Meta:
        table = "users"

    def __str__(self):
        return f"User {self.user_id} : {self.username}"


class Room(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=12, null=False)
    number = fields.IntField(null=False, unique=True)
    budget = fields.CharField(max_length=12, null=False)
    created_at = fields.DatetimeField(auto_now_add=True)
    is_closed = fields.BooleanField(default=False)
    started_at = fields.DatetimeField(null=True)
    closed_at = fields.DatetimeField(null=True)
    owner = fields.ForeignKeyField(
        'models.User',
        related_name='room_owner'
    )
    members = fields.ManyToManyField(
        'models.User',
        related_name='members',
        through='rooms_users',
        on_delete='CASCADE'
    )

    class Meta:
        table = "rooms"

    def __str__(self):
        return f"Room {self.number}: {self.name}"


class Wish(Model):
    id = fields.IntField(pk=True)
    wish = fields.CharField(max_length=256, null=False)
    room = fields.ForeignKeyField('models.Room', related_name='room',
                                  on_delete='CASCADE')
    user = fields.ForeignKeyField(
        'models.User',
        related_name='wishes_of_owner'
    )

    class Meta:
        table = "wishes"
        unique_together = (("room", "user"),)

    def __str__(self):
        return f"Room {self.room}: {self.user}"


class GameResult(Model):
    id = fields.IntField(pk=True)
    room = fields.ForeignKeyField(
        'models.Room',
        related_name='results_of_rooms'
    )
    recipient = fields.ForeignKeyField(
        'models.User',
        related_name='recipients'
    )
    sender = fields.ForeignKeyField(
        'models.User',
        related_name='senders'
    )
    assigned_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "game_results"

    def __str__(self):
        return f"Room {self.room}: {self.recipient} {self.sender}"
