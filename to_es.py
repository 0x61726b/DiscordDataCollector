from database import *
import datetime
import requests
import json

#KAIROS_SERVER = "http://localhost:8000"
ES_SERVER_MESSAGECOUNT = "http://40.121.158.220:9200/discord_reindex/discord_message_count/"
ES_SERVER_WORDS = "http://40.121.158.220:9200/discord_words/word_type/"

def add_message_count(message):
    timestamp = (int((message.date - datetime.datetime(1970, 1, 1)).total_seconds()))

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