# bot.py
import os
import random
import discord
from dotenv import load_dotenv
from discord.ext import commands
from discord.utils import get
from tabulate import tabulate

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='%')

import sqlite3
conn = sqlite3.connect(os.getenv('DB')) # open database connection
cursor = conn.cursor()
# conn.close()  # close database connection

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
            cursor.execute(f"INSERT INTO rating (member_id, member_name) VALUES ({member.id}, '{member.name}')")
            conn.commit()
            await member.add_roles(role) # add league role
            await ctx.send(f"{member.name} has been registered in league")
     except: # simple error handler if bot tries to insert duplicated value
         await ctx.send(f"It seems that {member.name} has rating assigned already but has no league role")

@bot.command(name='status', help=' - check your personal rating')
@commands.has_role('league')
async def status(ctx):
    # cursor.execute(f'SELECT rating,games,wins,ties,losses FROM rating WHERE member_id={ctx.author.id}')
    # data = cursor.fetchall()
    # await ctx.send(f"{data}")
    table=[["rating","games","wins","ties","losses"]]
    for row in cursor.execute(f'SELECT rating,games,wins,ties,losses FROM rating WHERE member_id={ctx.author.id}'):
        table.append([row[0],row[1],row[2],row[3],row[4]])
        await ctx.send(f">\n{tabulate(table)}")

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

bot.run(TOKEN)
# %%