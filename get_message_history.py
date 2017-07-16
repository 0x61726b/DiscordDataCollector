import discord
import logging
from database import *
from to_es import *
import threading
import asyncio

logging.basicConfig(level=logging.WARN)
logger = logging.getLogger(__name__)

handler = logging.FileHandler(filename='satoshi.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

client = discord.Client()

def add_user_to_db(member):
    #user_info = None
    # try:
    #     user_info = await client.get_user_info(member.id)
    # except:
    #     pass
    avatar_url = ""
    isBot = False
    created_at = datetime.datetime(1970,1,1)
    avatar_url = ""
    discriminator = ""
    display_name = ""
    name = ""
    join_date = datetime.datetime(1970,1,1)
    try:
        avatar_url = member.avatar_url
        isBot = member.bot
        created_at = member.created_at
        discriminator = member.discriminator
        display_name = member.display_name
        name = member.name
        join_date = datetime.datetime(1970,1,1)
    except:
        pass
    try:
        join_date = member.joined_at
    except:
        pass

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
        logger.warning("Could not find user. Adding")
        try:
            user = add_user_to_db(message.author)
            if user is None:
                return
        except Exception as err:
            logger.error("Could not add user")
            logger.error(err)
    try:
        channel = Channel.select().where(Channel.channel_id==channel_id).get()
    except:
        logger.warning("Could not find channel. Adding")
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


async def data_future(i_channel_name, before):
    channels = client.get_all_channels()
    count = 0
    for channel in channels:
        count = 0
        fetch_limit = 5000000
        message_list = []
        if channel.name == i_channel_name:
            print("Channel: {}".format(channel.name))
            try:
                async for message in client.logs_from(channel, limit=fetch_limit, before=before):
                    count = count + 1
                    message_list.append(message)
                    if count % 1000:
                        progress = (count / fetch_limit) * 100
            except Exception as ex1:
                print(ex1)
                print("add_message_to_db failed")

            print("Gathering messages finished for {}".format(channel.name))
            print("Count {}".format(count))
            fetch_limit = count

            add_count = 0
            for message in message_list:
                if add_count % 100 == 0:
                    progress = (add_count / fetch_limit) *100
                    print("Progress: - {} - {}".format(i_channel_name, float(progress)))
                try:
                    add_message_to_db(message)
                except Exception as ex:
                    print(ex)
                    print("add_message_to_db failed")
                add_count = add_count + 1
            progress = 0
            if fetch_limit is not 0:
                progress = (add_count / fetch_limit) * 100
            print("Progress: - {} - {}".format(i_channel_name, float(progress)))
            print("Finished adding messages to DB - channel {}".format(i_channel_name))

@client.event
async def on_ready():
    logger.info("Bot is ready.")
    before_date = datetime.datetime(2017,7,18)


    tasks =  [data_future("general-chat",before_date)]
    asyncio.ensure_future(asyncio.gather(*tasks))



with open("token", "r") as tokenfile:
    token = ""
    for line in tokenfile:
        token += line
    try:
        client.run(token)
    except Exception as ex:
        print(ex)
        print("Run threw exception")