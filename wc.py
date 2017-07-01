
from to_es import *
from collections import OrderedDict
from wordcloud import WordCloud

# Read the whole text.
text = ""



ignore_words = ["breast",
                "boob",
                "i",
                "the",
                "a",
                "to",
                "I",
                "it",
                "you",
                "of",
                "and",
                "that",
                "in",
                "for",
                "by",
                "on",
                "my",
                "was",
                "me",
                "ago",
                "is",
                "just",
                "but",
                "this",
                "its",
                "like",
                "want",
                "what",
                "im",
                "so",
                "have",
                "with",
                "if",
                "yeah",
                "they",
                "album",
                "metal",
                "too",
                "be",
                "to",
                "we",
                "or",
                "up",
                "oh",
                "do",
                "lol",
                "song",
                "get",
                "he",
                "she",
                "her",
                "his",
                "now",
                "dont",
                "why",
                "not",
                "one",
                "listen",
                "can",
                "wanna",
                "good",
                "shit",
                "not",
                "your",
                "can",
                "wanna",
                "did",
                "more",
                "here",
                "about",
                "at",
                "from",
                "out",
                "then",
                "it's",
                "because",
                "yes",
                "as",
                "him",
                "has",
                "had",
                "im",
                "I'm",
                "all",
                "Generating",
                "are"]


def get_cloud_by_user(id):
    messages = get_all_messages()

    word_count_map = dict()
    for message in messages:
        if message.user.discord_id == id:
            words = message.content.split()
            if len(words) > 0:
                for word in words:
                    if not word in ignore_words:
                        if word in word_count_map:
                            word_count_map[word] = word_count_map[word] + float(1)
                        else:
                            word_count_map[word] = float(0)

    word_count_map = OrderedDict(sorted(word_count_map.items(), reverse=True, key=lambda x: x[1]))

    wordcloud = WordCloud(width=1280, height=720).generate_from_frequencies(word_count_map, 240)
    #
    image = wordcloud.to_image()
    image.show()
    image.save("image.jpg", "JPEG")

def get_full_cloud():
    messages = get_all_messages()

    word_count_map = dict()
    for message in messages:
        words = message.content.split()
        if len(words) > 0:
            for word in words:
                if not word in ignore_words:
                    if word in word_count_map:
                        word_count_map[word] = word_count_map[word] + float(1)
                    else:
                        word_count_map[word] = float(0)


    word_count_map = OrderedDict(sorted(word_count_map.items(),reverse=True, key=lambda x: x[1]))

    count = 0
    for key,value in word_count_map.items():
        print("{} - {}".format(key, value))
        if count >= 500:
            break
        count = count + 1

    wordcloud = WordCloud(width = 1280, height=720).generate_from_frequencies(word_count_map,240)
    #
    image = wordcloud.to_image()
    image.show()
    image.save("image.jpg", "JPEG")



get_cloud_by_user(186622393219940354)