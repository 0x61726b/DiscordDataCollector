from peewee import *
from config import *
db = SqliteDatabase(DB_FILE + '.db')

class User(Model):
    discord_id = IntegerField(primary_key=True)
    avatarUrl = CharField()
    isBot = BooleanField()
    registerDate = DateTimeField()
    name = CharField()
    display_name = CharField()
    joinDate = DateTimeField()
    discriminator = IntegerField()
    #
    class Meta:
        database = db

class Channel(Model):
    channel_id = IntegerField(primary_key=True)
    name = CharField()
    topic = CharField()
    is_voice = BooleanField()

    class Meta:
        database = db

class Message(Model):
    message_id = IntegerField(primary_key=True)
    content = CharField()
    user = ForeignKeyField(User, related_name="users")
    channel = ForeignKeyField(Channel, related_name="channels")
    date = DateTimeField()
    is_pinned = BooleanField()
    has_mentions = BooleanField()

    class Meta:
        database = db


try:
    db.connect()
    db.create_tables([ User, Channel, Message ])
    print("DB OK!")
except:
    print("DB Not OK but still fine!")
    pass