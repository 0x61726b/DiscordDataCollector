import discord
import asyncio
import logging
from database import *
from to_es import *
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

handler = logging.FileHandler(filename='satoshi.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


class Presence():
    def __init__(self):
        self.canSetPresence = True

    def presence(self):
        return self.canSetPresence

    def setPresence(self,v):
        self.canSetPresence = v

p = Presence()
client = discord.Client()

async def add_user_to_db(member):
    user_info = await client.get_user_info(member.id)
    avatar_url = user_info.avatar_url
    isBot = user_info.bot
    created_at = user_info.created_at
    discriminator = user_info.discriminator
    display_name = user_info.display_name
    name = user_info.name
    join_date = member.joined_at

    logger.info("Adding new user to DB {} {} {} {} {} {} {} {}".format(member.id,name,display_name,join_date,created_at,isBot,avatar_url,discriminator))

    try:
        return User.create(discord_id=int(member.id),avatarUrl=avatar_url,isBot=isBot,registerDate=created_at,discriminator=discriminator,display_name=display_name,name=name,joinDate=join_date)
    except Exception as error:
        logger.debug("User.create failed. Probably due to primary key already existing. {}".format(error))
        return None


def add_channel_to_db(channel):
    channel_name = channel.name
    channel_id = channel.id
    topic = "" if channel.topic == None else channel.topic
    is_voice = False
    try:
        if channel.type == "voice":
            is_voice = True
    except:
        is_voice = False


    logger.info("Adding new channel to DB {} {}".format(channel_id,channel_name))

    try:
        return Channel.create(channel_id=int(channel_id),name=channel_name,topic=topic,is_voice=is_voice)
    except Exception as error:
        logger.info("Channel.create failed. {}".format(error))
        return None

def add_message_to_db(message):
    content = message.content
    message_id = int(message.id)
    user_id = int(message.author.id)
    channel_id = int(message.channel.id)
    date = message.timestamp
    has_mentions = False
    is_pinned = message.pinned

    try:
        user = User.select().where(User.discord_id==user_id).get()
    except:
        logger.info("Could not find user. Adding")
        user = add_user_to_db(message.author)
        if user is None:
            return
    try:
        channel = Channel.select().where(Channel.channel_id==channel_id).get()
    except:
        logger.info("Could not find channel. Adding")
        channel = add_channel_to_db(message.channel)
        if channel is None:
            logger.error("Channel error")
            return


    if len(message.mentions) != 0:
        has_mentions = True

    logger.info("New message: {} {} {} {} {}".format(user_id, user.name, user.display_name, channel.name, content))

    try:
        message = Message.create(message_id=message_id,content=content,user=user, channel=channel, date=date,has_mentions=has_mentions,is_pinned=is_pinned)
        add_message_count(message)
    except Exception as error:
        logger.debug("Message.create failed. Probably due to primary key already existing. {}".format(error))

@client.event
async def on_member_join(member):
    logger.info("New member join!")

    add_user_to_db(member)


@client.event
async def on_ready():
    logger.info("Bot is ready.")

    # If users table is empty, add users
    users = User.select()
    channels = Channel.select()

    if len(users) == 0:
        for member in client.get_all_members():
            await add_user_to_db(member)

    if len(channels) == 0:
        for channel in client.get_all_channels():
            add_channel_to_db(channel)

@client.event
async def on_message(message):
    if p.presence():
        logger.info("Setting presence...")
        await client.change_presence(game=discord.Game(name='Building Skynet...'))
        p.setPresence(False)

    add_message_to_db(message)


with open("token", "r") as tokenfile:
    token = ""
    for line in tokenfile:
        token += line
    client.run(token)