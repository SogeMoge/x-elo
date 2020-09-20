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
            embed = discord.Embed(title="Registration successful\nWelcome to the league!", colour=discord.Colour(0x6790a7))
            embed.set_footer(text=member.name, icon_url = member.avatar_url)
            await ctx.send(embed=embed)
            # await ctx.send(f"{member.name} has been registered in league")
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

@bot.command(name='game', help='submit results like @opponent and his result "@opponent win/loss"')
@commands.has_role('league')
async def results(ctx, member: discord.Member, result, points):
    pt = points
    # extract current values for author
    for a_row in cursor.execute(f'SELECT rating FROM rating WHERE member_id={ctx.author.id}'):
        Ra = a_row[0] # current author rating
        # a_games = a_row[1]
        # a_wins = a_row[2]
        # a_losses = a_row[3]

    # extract current values for opponent
    for op_row in cursor.execute(f'SELECT rating FROM rating WHERE member_id={member.id}'):
        Rop = op_row[0] # current opponent rating
        # op_games = op_row[1]
        # op_wins = op_row[2]
        # op_losses = op_row[3]
 

    if result in 'win':
        # calculating ELO
        ## gathered delta points from current game
        Ea = round( 1 / ( 1 + 10 ** ((Rop - Ra) / 400)), 2) # delta for author
        Eop = round( 1 / ( 1 + 10 ** ((Ra - Rop) / 400)), 2) # delta for opponent

        ## update rating
        Rna = round( Ra + 16 * (0 - Ea), 2) # Calculate new Ra as Rna, 0 for loss
        Rnop = round( Rop + 16 * (1 - Eop), 2) # Calculate new Rop as Rnop, 1 for win

        ## Create loss game entry for author
        cursor.execute(f'INSERT INTO games (id,member_id,opponent_id,result,score) VALUES(5,{ctx.author.id},{member.id},"loss","{pt}")')
        conn.commit()
        cursor.execute(f'UPDATE rating SET rating = {Rna}, games = games + 1, losses = losses + 1 where member_id={ctx.author.id}')
        conn.commit()

        # Create win game entry for opponent
        cursor.execute(f'INSERT INTO games (id,member_id,opponent_id,result,score) VALUES(5,{member.id},{ctx.author.id},"win","{pt}")')
        conn.commit()
        cursor.execute(f'UPDATE rating SET rating = {Rnop}, games = games + 1, wins = wins + 1 where member_id={member.id}')
        conn.commit()

        await ctx.send(f"{member.name} won with {points}!")
        for row in cursor.execute(f'SELECT rating FROM rating WHERE member_id={ctx.author.id}'):
            embed = discord.Embed(title="Updated League profile", colour=discord.Colour(0x6790a7))
            embed.add_field(name="Rating", value=row[0], inline=False)
            embed.set_footer(text=ctx.author.name, icon_url = ctx.author.avatar_url)
            await ctx.send(embed=embed)
        for row in cursor.execute(f'SELECT rating FROM rating WHERE member_id={member.id}'):
            embed = discord.Embed(title="Updated League profile", colour=discord.Colour(0x6790a7))
            embed.add_field(name="Rating", value=row[0], inline=False)
            embed.set_footer(text=member.name, icon_url = member.avatar_url)
            await ctx.send(embed=embed)

    elif result in 'loss':
        # calculating ELO
        ## gathered delta points from current game
        Ea = round( 1 / (1 + 10 ** ((Rop - Ra) / 400)) )
        Eop = round( 1 / (1 + 10 ** ((Ra - Rop) / 400 )) )

        ## update rating
        Rna = round( Ra + 16 * (1 - Ea) ) # Calculate new Ra as Rna, 1 for win
        Rnop = round( Rop + 16 * (0 - Eop) ) # Calculate new Rop as Rnop, 0 for loss

        # Create win game entry for author
        cursor.execute(f'INSERT INTO games (id,member_id,opponent_id,result,score) VALUES(5,{ctx.author.id},{member.id},"win","{pt}")')
        conn.commit()
        # update rating and game statistics
        cursor.execute(f'UPDATE rating SET rating = {Rna}, games = games + 1, wins = wins + 1 where member_id={ctx.author.id}')
        conn.commit()

        # Create loss game entry for opponent
        cursor.execute(f'INSERT INTO games (id,member_id,opponent_id,result,score) VALUES(5,{member.id},{ctx.author.id},"loss","{pt}")')
        conn.commit()
        # update rating and game statistics
        cursor.execute(f'UPDATE rating SET rating = {Rnop}, games = games + 1, losses = losses + 1 where member_id={member.id}')
        conn.commit()

        await ctx.send(f'{ctx.author.name} won with {points}!')
        for row in cursor.execute(f'SELECT rating FROM rating WHERE member_id={ctx.author.id}'):
            embed = discord.Embed(title="Updated League profile", colour=discord.Colour(0x6790a7))
            embed.add_field(name="Rating", value=row[0], inline=False)
            embed.set_footer(text=ctx.author.name, icon_url = ctx.author.avatar_url)
            await ctx.send(embed=embed)
        for row in cursor.execute(f'SELECT rating FROM rating WHERE member_id={member.id}'):
            embed = discord.Embed(title="Updated League profile", colour=discord.Colour(0x6790a7))
            embed.add_field(name="Rating", value=row[0], inline=False)
            embed.set_footer(text=member.name, icon_url = member.avatar_url)
            await ctx.send(embed=embed)
    else:
        await ctx.send(f'Wrong result!')


@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

bot.run(TOKEN)
# %%