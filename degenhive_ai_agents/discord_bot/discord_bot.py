from telegram import Bot
from typing import Final
from dotenv import load_dotenv
from discord import Intents, Client, Message
# from responses import get_response
import requests
import os
import json

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

intents = Intents.default()
# intents.message_count = True
# intents.typing = False
# intents.presences = False
client = Client(intents=intents)


async def send_discord_message(message: Message, user_message: str):
    if not user_message:
        print("No message to send")
        return
        
    is_private = user_message[0] == '?'
    if is_private:
        user_message = user_message[1:]

    try: 
        response: str = get_discord_response(user_message)
        # Send message to user in private if its a private message else send it in the channel
        # await message.author.send(response) if is_private else await message.channel.send(response)
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


def main() -> None:
    client.run(DISCORD_TOKEN)



if __name__ == "__main__":


    with open(f"./referral_codes.json") as json_file:  
      invite_codes_list = json.load(json_file)

    main()