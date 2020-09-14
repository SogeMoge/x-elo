# bot.py
import os
import random
import sqlite3

import discord
from dotenv import load_dotenv

from discord.ext import commands
from discord.utils import get

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='%')

# @bot.command(name='полом', help=' - Мяукнет в ответ')
# async def mew(ctx):
#     mew_sound = ['Кошечка говорит мяу']

#     response = random.choice(mew_sound)
#     await ctx.send(response)


@bot.command(name='reg', help=' - apply league role to a user')
@commands.has_role('league admin')
async def giverole(ctx, member: discord.Member):
    try:
        role = get(ctx.guild.roles, name="league") # role you want to add to a user
        if role in member.roles:                   # checks if user has such role
            await ctx.send(f"{member.name} has league role already")
        else:
            conn = sqlite3.connect(os.getenv('DB')) # open database connection
            cursor = conn.cursor()
            sql = "INSERT INTO rating (user_id, user_name) VALUES (?, ?)"
            id = member.id
            name = member.name
            cursor.execute(sql, [id, name])
            conn.commit()
            conn.close()  # close database connection
            await member.add_roles(role) # add league role
            await ctx.send(f"{member.name} has been registered in league")
    except: # simple error handler if bot tries to insert duplicated value
        await ctx.send(f"It seems that {member.name} has rating assigned already but has no league role")

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

bot.run(TOKEN)
# %%