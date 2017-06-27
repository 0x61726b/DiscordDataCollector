from database import *
import datetime
import requests
import json

#KAIROS_SERVER = "http://localhost:8000"
ES_SERVER = "http://127.0.0.1:9200/discord/discord_message_count/"
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
        response = requests.put("{}{}".format(ES_SERVER, message.message_id), data, headers= headers)
        print("Added {} {}".format(timestamp, message.message_id))
        print(response.status_code)
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