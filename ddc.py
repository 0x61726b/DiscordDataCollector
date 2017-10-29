import discord
import asyncio
import logging
from database import *
from to_es import *
import os
import sys
import inspect
import random
from random import randint
random.seed(8088)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

handler = logging.FileHandler(filename='satoshi.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

class Response:
    def __init__(self, content, reply=False, delete_after=0):
        self.content = content
        self.reply = reply
        self.delete_after = delete_after

PREFIX = "!"

class MessageState:
    def __init__(self, time, user):
        self.time = time
        self.user = user

class DDC(discord.Client):
    def __init__(self,token):
        self.auth = token
        super().__init__()

        self.queue = asyncio.Queue()

    async def get_random_message(self, client_id):
        try:
            target_user = User.select().where(User.discord_id == client_id).get()
            message_array = []
            messages = Message.select().order_by(Message.date).where((Message.channel != EXCLUDE_CHANNEL_ID),(Message.user == target_user.discord_id))
            for message in messages:
                message_array.append(message)

            unqualified = True
            random_msg = None

            len_messages = len(message_array)
            max_iterations = len_messages - 1
            i = 0
            while unqualified:
                random_nmb = randint(0, len_messages - 1)
                random_msg = message_array[random_nmb]
                if random_msg:
                    if "<:" in random_msg.content or len(random_msg.content) < 50 or "<@" in random_msg.content or "://" in random_msg.content or len(random_msg.content) > 1000 or "```" in random_msg.content:
                        unqualified = True
                    else:
                        unqualified = False
                i = i + 1

                if i > max_iterations:
                    unqualified = False
                    random_msg = None
            if random_msg:
                content = random_msg.content
                user_id = random_msg.user.discord_id
                user_info = await self.get_user_info(user_id)
                if user_info:
                    content = "```xml\n[{}/{}] <{}> {}```".format(random_nmb, len_messages, user_info.display_name,content)
            else:
                content = ""
            return content
        except:
            return ""

    async def cmd_q(self, message, channel):
        try:
            split = message.content.split('{}{} '.format(PREFIX, 'q'))
            user_name = split[1]

            clients = self.get_all_members()
            target_client = None
            for client in clients:
                id = client.id
                name = client.name

                if name.lower() == user_name.lower():
                    target_client = client
            if target_client:
                random_msg = await self.get_random_message(target_client.id)
                if len(random_msg) > 0:
                    await self.send_message(channel, random_msg)
                else:
                    await self.send_message(channel, EMOJI_ON_FAIL)
        except:
            pass

    async def random_msg_task(self):
        await self.wait_until_ready()
        channel = self.get_channel(RANDOM_QUOTE_TARGET_CHANNEL_ID)

        last_message_time = datetime.datetime.now()
        last_message_user = None
        should_post = False

        interval = RANDOM_QUOTE_INTERVAL

        print("Starting random msg task")

        while not self.is_closed:
            qsize = self.queue.qsize()

            if qsize != 0:
                while qsize is not 0:
                    message_state = await self.queue.get()
                    if message_state:
                        last_message_user = message_state.user

                    qsize = self.queue.qsize()

            now = datetime.datetime.now()
            diff = now - last_message_time

            if diff.total_seconds() > interval:
                should_post = True

            if last_message_user is not None and last_message_user.id == BOT_CLIENT_ID:
                should_post = False
            if should_post:
                users = User.select()
                users_array = []
                last_message_time = datetime.datetime.now()
                should_post = False

                try:
                    for user in users:
                        users_array.append(user)

                    users_len = len(users_array)
                    random_user_index = randint(0, users_len - 1)
                    random_user = users_array[random_user_index]
                    if random_user and random_user.discord_id != BOT_CLIENT_ID:
                        try:
                            random_msg = await self.get_random_message(random_user.discord_id)
                            if len(random_msg) > 0:
                                await self.send_message(channel, random_msg)
                                await asyncio.sleep(5)
                            else:
                                await asyncio.sleep(5)
                        except:
                            await asyncio.sleep(5)
                except:
                    await asyncio.sleep(5)
            else:
                await asyncio.sleep(5)




    async def on_ready(self):
        logger.info("Bot is ready.")

        try:
            await self.change_presence(game=discord.Game(name='Music sucks'))
        except:
            logging.warning("Could not set presence")
    async def on_member_join(self,member):
        await self.add_user_to_db(member)
    async def add_user_to_db(self,member):
        user_info = await self.get_user_info(member.id)
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
    async def add_channel_to_db(self,channel):
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
    async def add_message_to_db(self,message):
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
            user = await self.add_user_to_db(message.author)
            if user is None:
                return
        try:
            channel = Channel.select().where(Channel.channel_id==channel_id).get()
        except:
            logger.info("Could not find channel. Adding")
            channel = self.add_channel_to_db(message.channel)
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
    async def on_message(self, message):
        message_content = message.content.strip()

        await self.add_message_to_db(message)
        await self.queue.put(MessageState(datetime.datetime.now(),message.author))
        qsize = self.queue.qsize()

        if not message_content.startswith(PREFIX):
            return

        command, *args = message_content.split()
        command = command[len(PREFIX):].lower().strip()

        handler = getattr(self, 'cmd_%s' % command, None)
        if not handler:
            return

        argspec = inspect.signature(handler)
        params = argspec.parameters.copy()

        try:
            handler_kwargs = {}
            if params.pop('message', None):
                handler_kwargs['message'] = message

            if params.pop('channel', None):
                handler_kwargs['channel'] = message.channel

            if params.pop('author', None):
                handler_kwargs['author'] = message.author

            if params.pop('server', None):
                handler_kwargs['server'] = message.server

            if params.pop('user_mentions', None):
                handler_kwargs['user_mentions'] = list(map(message.server.get_member, message.raw_mentions))

            if params.pop('channel_mentions', None):
                handler_kwargs['channel_mentions'] = list(map(message.server.get_channel, message.raw_channel_mentions))

            args_expected = []
            for key, param in list(params.items()):
                doc_key = '[%s=%s]' % (key, param.default) if param.default is not inspect.Parameter.empty else key
                args_expected.append(doc_key)

                if not args and param.default is not inspect.Parameter.empty:
                    params.pop(key)
                    continue

                if args:
                    arg_value = args.pop(0)
                    handler_kwargs[key] = arg_value
                    params.pop(key)

            response = await handler(**handler_kwargs)

            if response and isinstance(response, Response):
                content = response.content
                if response.reply:
                    content = '%s, %s' % (message.author.mention, content)

                sentmsg = await self.safe_send_message(
                    message.channel, content,
                    expire_in=response.delete_after
                )
        except Exception as ex:
            logger.error("Error handling command")
            content = "I've run into a problem while processing your command"
            sentmsg = await self.safe_send_message(
                message.channel, content,
                expire_in=10
            )
            print(ex)
    async def safe_send_message(self, dest, content, *, tts=False, expire_in=0, also_delete=None, quiet=False):
        msg = None
        try:
            msg = await self.send_message(dest, content, tts=tts)

            if msg and expire_in:
                asyncio.ensure_future(self._wait_delete_msg(msg, expire_in))

            if also_delete and isinstance(also_delete, discord.Message):
                asyncio.ensure_future(self._wait_delete_msg(also_delete, expire_in))

        except discord.Forbidden:
            if not quiet:
                self.safe_print("Warning: Cannot send message to %s, no permission" % dest.name)

        except discord.NotFound:
            if not quiet:
                self.safe_print("Warning: Cannot send message to %s, invalid channel?" % dest.name)

        return msg
    async def _wait_delete_msg(self, message, after):
        await asyncio.sleep(after)
        await self.safe_delete_message(message)
    async def safe_delete_message(self, message, *, quiet=False):
        try:
            return await self.delete_message(message)

        except discord.Forbidden:
            if not quiet:
                self.safe_print("Warning: Cannot delete message %s no permission" % message.clean_content)

        except discord.NotFound:
            if not quiet:
                self.safe_print("Warning: Cannot delete message %s message not found" % message.clean_content)
    def run(self):
        try:
            self.loop.create_task(self.random_msg_task())
            self.loop.run_until_complete(self.start(self.auth))
        except discord.errors.LoginFailure:
            logger.error("Login error")

        finally:
            logger.info("Exiting...")
            self.loop.close()


if __name__ == '__main__':
    try:
        with open("token", "r") as tokenfile:
            token = ""
            for line in tokenfile:
                token += line
            bot = DDC(token)
            bot.run()
    except KeyboardInterrupt as ex:
        print("Keyboard interrupted")
        sys.exit(0)