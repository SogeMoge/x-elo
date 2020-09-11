# bot.py
import os
import random

import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')


client = discord.Client()

@client.event
async def on_ready():
    print(f'{client.user.name} is connected to the Discord!')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    mew = [
        'МЯУ',
        'МЯ',
        'МЯЯУУ'
    ]

    if message.content == 'полом':
        response = random.choice(mew)
        await message.channel.send(response)

client.run(TOKEN)
# %%