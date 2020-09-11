# bot.py
import os
import random

import discord
from dotenv import load_dotenv

# 1
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# 2
bot = commands.Bot(command_prefix='%')

@bot.command(name='полом', help=' - Мяукнет в ответ')
async def mew(ctx):
    mew_sound = ['Кошечка говорит мяу']

    response = random.choice(mew_sound)
    await ctx.send(response)

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

bot.run(TOKEN)
# %%