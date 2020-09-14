# bot.py
import os
import random

import discord
from dotenv import load_dotenv

# 1
from discord.ext import commands
from discord.utils import get

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# 2
bot = commands.Bot(command_prefix='%')

# @bot.command(name='полом', help=' - Мяукнет в ответ')
# async def mew(ctx):
#     mew_sound = ['Кошечка говорит мяу']

#     response = random.choice(mew_sound)
#     await ctx.send(response)

@bot.command(name='reg', help=' - apply league role to a user')
@commands.has_role('league admin')
async def giverole(ctx, member: discord.Member):
    role = get(ctx.guild.roles, name="league") # role you want to add to a user
    if role in member.roles:                   # checks if user has such role
        await member.remove_roles(role)        #removes the role
    else:
        await member.add_roles(role)
        await ctx.send(f"{member.name} has been registered in league")

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

bot.run(TOKEN)
# %%