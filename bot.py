# bot.py
import os
import random
import discord
from dotenv import load_dotenv
from discord.ext import commands
from discord.utils import get

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


@bot.command(name='register', help=' - apply league role to a user', aliases=['reg'])
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

@bot.command(name='status', help=' - check your personal rating', aliases=['stat'])
@commands.has_role('league')
async def status(ctx):
    for row in cursor.execute(f'SELECT rating,games,wins,losses FROM rating WHERE member_id={ctx.author.id}'):
        embed = discord.Embed(title="League profile", colour=discord.Colour(0x6790a7))
        embed.add_field(name="Rating", value=row[0], inline=False)
        embed.add_field(name="Games", value=row[1], inline=True)
        embed.add_field(name="Wins", value=row[2], inline=True)
        embed.add_field(name="Losses", value=row[3], inline=True)
        embed.set_footer(text=ctx.author.name, icon_url = ctx.author.avatar_url)
        await ctx.send(embed=embed)

@bot.command(name='game', help='submint game results in form of "@winner win @looser loss"')
@commands.has_role('league')
async def results(ctx, member: discord.Member):
            await bot.send_message()


@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

bot.run(TOKEN)
# %%