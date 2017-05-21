import networkx as nx
import matplotlib.pyplot as plt
from peewee import *
import datetime
import random

db = SqliteDatabase('metal_music_discord.db')

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

db.connect()

users = User.select()

date_count = len(users)

x = [u.joinDate for u in users]
y = [i for i in range(date_count)]

x.sort(key=lambda r: r)

plt.plot(x,y)
plt.gcf().autofmt_xdate()

plt.show()