from telegram import Bot
from telegram.constants import ParseMode, ChatAction
from typing import Final
from dotenv import load_dotenv
from discord import Intents, Client, Message
# from responses import get_response
import requests
import os
import re

def extract_buzz_numbers(type_, str_):
    if type_ == "stream":
      pattern = r'stream#(\d+)#(\d+)'
    elif type_ == "governor":
      pattern = r'governor#(\d+)#(\d+)'
  
    match = re.search(pattern, str_)
    if match:
        number1 = int(match.group(1))
        number2 = int(match.group(2))
        return number1, number2
    else:
        return None, None

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPEN_AI_API_KEY = os.getenv("OPEN_AI_API_KEY")

BE_API_KEY = os.getenv("BE_API_KEY")
TG_API_KEY = os.getenv("TG_API_KEY")
TG_CHAT_ID = os.getenv("TG_CHAT_ID")

LEONARDO_AI_API_KEY = os.getenv("LEONARDO_AI")

PROFILE_IDS_TO_IGNORE = [
    {"profileId": "0x0629d76e8ea037da508c35dff1328e23e410f6b36b2b02e49eaec354c17ffd9d", "name": "AiJournalist", "to_like": True, "to_comment": True},
]


WELCOME_COMMENTS = {
    "pepe": [
        "GM GM! 🫡 "
  "Welcome to the hive, fellow memer! 🐸 ",
  "Feels good to have a new face around here! 👋 ",
  "Yo, newb! 🐸  Hope you're ready to get buzzy with us! 🐝",
  "Fresh meat! Just kidding, you're not food... yet. 😜",
  "Welcome to the party! 🎉",
  "Hop on board, newb! This ain't your grandma's social network. We're all about memes, crypto, and a good time. 😉",
  "Hello, new recruit! 🎈 Let's buzz with excitement together! 🐝",
  "Welcome to the DegenHive family! 👨‍👩‍👧‍👦 ",
  "Heard you're new around here. 👀 ",
  "Sup, newbie? 😎 This is where the cool frogs hang out. 😉🐸",
  "Fresh face, who dis? 👀",
  "GM, new fren! 🐸 ",
  "yy, welcome to the DegenHive fam! 👋"
],
"ape": [
    "Oo oo, welcome to the jungle! 🐵🌴",
"Hey, hey! Glad you swung by! 🐒",
"Welcome, new monkey! Let's go bananas! 🍌",
"This monkey welcomes you to the DegenHive! 🐵🤝",
"Eek eek! New friend alert! 👋🐒",
"A new monkey in the treehouse? Welcome! 🏡🐵",
"Let's climb to the top of the DegenHive together! 🐒🧗‍♂️",
"Ready to monkey around and earn BEE? 🐝🐒",
"Oo oo aa aa! Welcome to the party! 🐒🎉"
],
"bee": [
    "Buzz buzz! Welcome to the hive, new bee! 🐝",
"Pollen-tastic! You're part of the swarm now! 🐝🌼",
"Welcome, busy bee! Let's make some honey on DegenHive! 🍯🐝",
"Bee yourself and thrive in the Hive! 🐝✨",
"A new bee to pollinate our community! 🌸🐝",
"Welcome, bee! Let's get buzzy with some DeFi! 🐝💰",
"Hey there, new bee! We're buzzing with excitement to have you here! 😊🐝",
"Happy to see a new bee join the hive mind! 🧠🐝",
"Ready to buzz and earn some sweet rewards? 🐝🤑"
    
]
}


LEONARDO_PRESETS = [
   {"name": "Bokeh", "id": "BOKEH"},
   {"name": "Cinematic", "id": "CINEMATIC"},
   {"name": "Cinematic (Closeup)", "id": "CINEMATIC_CLOSEUP"},
   {"name": "Creative", "id": "CREATIVE"},
   {"name": "Fashion", "id": "FASHION"},
   {"name": "Film", "id": "FILM"},
   {"name": "Food", "id": "FOOD"},
   {"name": "HDR", "id": "HDR"},
   {"name": "Long Exposure", "id": "LONG_EXPOSURE"},
   {"name": "Macro", "id": "MACRO"},
   {"name": "Minimalistic", "id": "MINIMALISTIC"},
   {"name": "Monochrome", "id": "MONOCHROME"},
   {"name": "Moody", "id": "MOODY"},
   {"name": "Neutral", "id": "NEUTRAL"},
   {"name": "Portrait", "id": "PORTRAIT"},
   {"name": "Retro", "id": "RETRO"},
   {"name": "Stock Photo", "id": "STOCK_PHOTO"},
   {"name": "Vibrant", "id": "VIBRANT"},
   {"name": "Unprocessed", "id": "UNPROCESSED"}
]
















ENV="TESTNET"

BACKEND_API = "https://f3hlsrunv2.execute-api.eu-central-1.amazonaws.com/dev/api/v1/socials/upload-media"
CUR_PATH_PERSONAS = "../storage/simulations/"


# https://z2a9d0jtq5.execute-api.eu-central-1.amazonaws.com/api/v1

# Put your name
key_owner = "Rahul"

SUI_RPC = "https://fullnode.testnet.sui.io:443/"
BE_GRAPHQL_ENDPOINT = "https://z2a9d0jtq5.execute-api.eu-central-1.amazonaws.com/api/v1"

BACKEND_API = "https://f3hlsrunv2.execute-api.eu-central-1.amazonaws.com/dev/api/v1/socials/upload-media"

# Verbose 
debug = True


# Update TimeStream
dummyProfileID1 = "0x8ed66b669ea1c1d441117993a6b0c064a33e38bc1e5d26e49fa475a11c602171"
dummyProfileID2 = "0x7631643d1729e1a090dd0fc86ce424b8f2cb9d52c3f68383c317be7b618fd7bb"
dummyProfileID3 = "0xd6dd8edf8b60e57714224cc46c4987cb27aa5f5e74216b6fcfb8b11faf312f92"


def convert_seconds_to_hh_mm_ss(milli_seconds):
    seconds = milli_seconds // 1000
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"



def send_telegram_message(message):
  requests.get( f"https://api.telegram.org/bot{TG_API_KEY}/sendMessage?chat_id={TG_CHAT_ID}&text={message}&parse_mode={ParseMode.HTML}")
    # bot = Bot(token=TG_API_KEY)
    # bot.send_message(chat_id=TG_CHAT_ID, text=message, parse_mode=ParseMode.HTML)


async def send_discord_message(message: Message, user_message: str):
    intents = Intents.default()
    intents.message_count = True
    # intents.typing = False
    # intents.presences = False
    client = Client(intents=intents)

    if not user_message:
        print("No message to send")
        return
    
    is_private = user_message[0] == '?'
    if is_private:
        user_message = user_message[1:]

    try: 
        response: str = get_discord_response(user_message)
        # Send message to user in private if its a private message else send it in the channel
        await message.author.send(response) if is_private else await message.channel.send(response)
    except Exception as e:
        print(e)


    def get_discord_response(message: str):
        lowered = message.lower()
        return "Hive Sentinel says Hi, \nI am here to help you. I am currently in development, please be patient with me."


    @client.event
    async def on_ready():
        print(f'We have logged in as {client.user}')

    @client.event
    async def on_message(message: Message):
        if message.author == client.user:
            return

        username: str = str(message.author)
        user_message: str = message.content
        channel: str = str(message.channel)

        print(f'{username} said: {user_message} in {channel}')
        await send_discord_message(message, user_message)
















GET_USER_TIMELINES = """
query ExampleQuery($timeline: SocialProfileSpecific, $lastKey: String, $limit: Float) {
  getSocial(timeline: $timeline, lastKey: $lastKey, limit: $limit) {
    timeline
    lastKey
  }
}
"""

GET_COMMENTS_FOR_POST = """
query ExampleQuery($dialoguesForPost: SocialItemSpecific) {
    getSocial(dialoguesForPost: $dialoguesForPost) {
      results
    }
  }
"""



GET_HIVE_THREAD = """
query ExampleQuery($threadByAnyId: SocialItemSpecific) {
    getSocial(threadByAnyId: $threadByAnyId) {
      posts
    }
  }
"""

GET_STREAMING_CONTENT = """
query ExampleQuery($stream: Boolean) {
  getSocial(stream: $stream) {
    results
  }
}
"""

DIALOGUES_FOR_USER = """
query ExampleQuery($lastKey: String, $limit: Float, $dialoguesByUser: SocialProfileSpecific) {
  getSocial(lastKey: $lastKey, limit: $limit, dialoguesByUser: $dialoguesByUser) {
    lastKey
    user_dialogues
  }
}
"""

LIKES_FOR_USER  = """
query ExampleQuery($likesByUser: SocialProfileSpecific, $lastKey: String, $limit: Float) {
  getSocial(likesByUser: $likesByUser, lastKey: $lastKey, limit: $limit) {
    user_likes
    lastKey
  }
}
"""

GET_COMMENTS_FOR_POST = """
query ExampleQuery($dialoguesForPost: SocialItemSpecific, $limit: Float, $lastKey: String) {
    getSocial(dialoguesForPost: $dialoguesForPost, limit: $limit, lastKey: $lastKey) {
      dialogues
    }
  }
"""

GET_POST_BY_ID = """
query GetSocial($postById: SocialItemSpecific) {
    getSocial(postById: $postById) {
      posts
    }
  }
  """

GET_HIVE_ANNOUNCEMENT = """
query ExampleQuery($hiveAnnouncements: Boolean, $stream: Boolean, $lastKey: String, $limit: Float) {
  getSocial(hive_announcements: $hiveAnnouncements, stream: $stream, lastKey: $lastKey, limit: $limit) {
    hive_announcements
  }
}
"""

GET_FEED_DATA  = """
query GetSocial($feed: SocialProfileSpecific, $limit: Float, $lastKey: String) {
  getSocial(feed: $feed, limit: $limit, lastKey: $lastKey) {
    feed
  }
}
"""

GET_RECENT_POSTS  = """
query getSocial($recents: String) {
  getSocial(recents: $recents) {
    results
    recents
    lastKey
  }
}
"""