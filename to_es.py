from database import *
import datetime
import requests
import json
import re
from config import *

#KAIROS_SERVER = "http://localhost:8000"
ES_SERVER_MESSAGECOUNT = ES_SERVER + ES_INDEX_MESSAGECOUNT
ES_SERVER_COMMANDS = ES_SERVER + ES_INDEX_COMMANDS
ES_SERVER_EMOJI = ES_SERVER + ES_INDEX_EMOJI
ES_SERVER_WORDS = ES_SERVER + ES_INDEX_WORDS

def add_emoji(message, emoji, index_id):
    timestamp = (int((message.date - datetime.datetime(1970, 1, 1)).total_seconds()))

    json_str = {"timestamp": timestamp,
                "message_id": message.message_id,
                "emoji": emoji,
                "emoji_count":1,
                "channel": message.channel.name,
                "author": message.user.name
                }
    headers = {'Content-Type': 'application/json'}
    data = json.dumps(json_str)
    try:
        response = requests.put("{}{}".format(ES_SERVER_EMOJI, index_id), data, headers=headers)
        if response.status_code == 201 or response.status_code == 200:
            print("Emoji - ES Successful {}".format(response.status_code))
    except Exception as error:
        print("Error trying to send data to ES")
        print(error)

def add_command(message,command):
    timestamp = (int((message.date - datetime.datetime(1970, 1, 1)).total_seconds()))

    json_str = {"timestamp": timestamp,
                "message_id": message.message_id,
                "command": command,
                "command_count":1,
                "channel": message.channel.name,
                "author": message.user.name
                }
    headers = {'Content-Type': 'application/json'}
    data = json.dumps(json_str)
    try:
        response = requests.put("{}{}".format(ES_SERVER_COMMANDS, message.message_id), data, headers=headers)
        if response.status_code == 201 or response.status_code == 200:
            print("Command - ES Successful {}".format(response.status_code))
    except Exception as error:
        print("Error trying to send data to ES")
        print(error)

def add_message_count(message):
    timestamp = (int((message.date - datetime.datetime(1970, 1, 1)).total_seconds()))

    # Check commands
    prefix = ["!", "~"]
    message_content = message.content
    for p in prefix:
        if not message_content.startswith(p):
            continue
        command, *args = message_content.split()
        command = command[len(p):].lower().strip()

        add_command(message, command)

    if CHECK_EMOJI:
        # Check emojis
        emojis = ["FeelsMetalMan", "goldMetal", "petaLUL", "PogChamp", "puke", "Eargasm", "EleGiggle", "FeelsBadMan",
                  "FeelsRageMan", "FeelsBlackMetal", "FeelsCoreMan",
                  "FeelsLongHaired", "FeelsCorpsePaint", "FeelsBleagh", "FeelsProgMan", "FeelsMetalHead", "thinkmetal",
                  "fedora", "trump1", "nm", "suicide", "slamslug", "arkhammer", "uberthink", "nerdal", "rip",
                  "thangery", "thunking", "grindgoat", "CoreWeekly", "CoreYearly", "pukethink1", "FeelsSubLevel",
                  "genrepolice", "FeelsAmazingMan", "FailFish", "WutFace", "FeelsWeebMan", "FeelsTootMan", "CoreEternity",
                  "FeelsNargaMan", "hmm", "glamslug", "FeelsCossackMan", "boing", "cutyou", "FeelsToneMan"]
        for emoji in emojis:
            str = "<:{}".format(emoji)

            matches = [m.start() for m in re.finditer(str, message_content)]
            if len(matches) > 0:
                i = 0
                for match in matches:
                    index = message.message_id
                    index = "{}{}".format(index, i)
                    add_emoji(message, emoji, int(index))
                    i = i + 1

    # message count stuff
    json_str = { "timestamp": timestamp,
                 "message_id": message.message_id,
                 "message_count": 1.0,
                 "channel": message.channel.name,
                 "author": message.user.name,
                 "word_count": float(len(message.content.split()))
                 }
    headers = { 'Content-Type': 'application/json' }
    data = json.dumps(json_str)
    try:
        response = requests.put("{}{}".format(ES_SERVER_MESSAGECOUNT, message.message_id), data, headers= headers)
        # if response.status_code == 201 or response.status_code == 200:
        #     print("ES Successful {}".format(response.status_code))
    except Exception as error:
        print("Error trying to send data to ES")
        print(error)

total_word_count = 0
def add_words(message):
    timestamp = (int((message.date - datetime.datetime(1970, 1, 1)).total_seconds()))

    for word in message.content.split():
        json_str = {"timestamp": timestamp,
                    "word": word
                    }
        headers = {'Content-Type': 'application/json'}
        data = json.dumps(json_str)
        try:
            response = requests.put("{}{}".format(ES_SERVER_WORDS, total_word_count), data, headers=headers)
            print("Added {} {} {}".format(timestamp, total_word_count, word))
            print(response.status_code)
            total_word_count = total_word_count + 1
        except Exception as error:
            print("Error trying to send data to ES")
            print(error)

def get_all_messages():
    return Message.select()

def put_messages_to_es():
    messages = get_all_messages()
    count = 0
    # for i in range(25):
    for message in messages:
        if count > 108893:
            print("Processing message {}".format(count))
            # message = messages[i]
            add_message_count(message)
        count = count + 1

def put_words_to_es():
    messages = get_all_messages()
    count = 0
    # for i in range(25):
    for message in messages:
        add_words(message)
        count = count + 1

def put_commands_to_es():
    messages = get_all_messages()

    prefix = ["!", "~"]
    for message in messages:
        message_content = message.content
        for p in prefix:
            if not message_content.startswith(p):
                continue
            command, *args = message_content.split()
            command = command[len(p):].lower().strip()

            add_command(message, command)

def put_emojis_to_es():
    messages = get_all_messages()

    emojis = ["FeelsMetalMan", "goldMetal", "petaLUL", "PogChamp", "puke", "Eargasm", "EleGiggle", "FeelsBadMan", "FeelsRageMan", "FeelsBlackMetal", "FeelsCoreMan",
              "FeelsLongHaired","FeelsCorpsePaint", "FeelsBleagh", "FeelsProgMan", "FeelsMetalHead", "thinkmetal", "fedora", "trump1", "nm", "suicide", "slamslug", "arkhammer", "uberthink", "nerdal", "rip",
              "thangery", "thunking", "grindgoat", "CoreWeekly", "CoreYearly", "pukethink1", "FeelsSubLevel", "genrepolice", "FeelsAmazingMan", "FailFish", "WutFace", "FeelsWeebMan", "FeelsTootMan", "CoreEternity", "FeelsNargaMan", "hmm", "glamslug", "FeelsCossackMan", "boing", "cutyou", "FeelsToneMan"]
    for message in messages:
        message_content = message.content

        for emoji in emojis:
            str = "<:{}".format(emoji)

            matches = [m.start() for m in re.finditer(str, message_content)]
            if len(matches) > 0:
                i = 0
                for match in matches:
                    index = message.message_id
                    index = "{}_{}".format(index,i)
                    add_emoji(message, emoji, index)
                    i = i + 1