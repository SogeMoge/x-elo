# bot.py
import os
import random
import discord

#load sensitive data from .env file
from dotenv import load_dotenv

from discord.ext import commands
from discord.utils import get

# load token from .env file
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()

# set prefix for bot commands
bot = commands.Bot(command_prefix='%')

# open connection to database
import sqlite3
conn = sqlite3.connect(os.getenv('DB'))
cursor = conn.cursor()
# conn.close()  # close database connection

reactions = ['✅','❎']

######################
# @bot.command(name='полом', help=' - Мяукнет в ответ')
# async def mew(ctx):
#     mew_sound = ['Кошечка говорит мяу']

#     response = random.choice(mew_sound)
#     await ctx.send(response)
######################

@bot.command(name='register', help=' - apply league role to a user', aliases=['reg'])
@commands.has_role('league admin')
async def giverole(ctx, member: discord.Member):
     try:
        role = get(ctx.guild.roles, name="league")                    # role you want to add to a user
        if role in member.roles:                                      # checks if user has such role
            await ctx.send(f"{member.name} has league role already")
        else:
            # Inserts row with user data into db as well as default game stat values
            cursor.execute(f"INSERT INTO rating (member_id, member_name) VALUES ({member.id}, '{member.name}')")
            conn.commit()

            # add league role
            await member.add_roles(role)
            # pretty outpun in chat
            embed = discord.Embed(title="Registration successful\nWelcome to the league!", colour=discord.Colour(0x6790a7))
            embed.set_footer(text=member.name, icon_url = member.avatar_url)
            await ctx.send(embed=embed)
     except: # simple error handler if bot tries to insert duplicated value
         await ctx.send(f"It seems that {member.name} has rating assigned already but has no league role")

# command outputs game statistics for author of the command
@bot.command(name='status', help=' - check your personal rating', aliases=['stat'])
@commands.has_role('league')
async def status(ctx):
    for row in cursor.execute(f'SELECT rating,games,wins,losses FROM rating WHERE member_id={ctx.author.id}'):
        embed = discord.Embed(title="League profile", colour=discord.Colour(0xFFD700))
        embed.add_field(name="Rating", value=row[0], inline=False)
        embed.add_field(name="Games", value=row[1], inline=True)
        embed.add_field(name="Wins", value=row[2], inline=True)
        embed.add_field(name="Losses", value=row[3], inline=True)
        embed.set_footer(text=ctx.author.name, icon_url = ctx.author.avatar_url)
        await ctx.send(embed=embed)

# command outputs game statistics for author of the command
@bot.command(name='check', help=' - check how many games you played with tagged user', aliases=['chk'])
@commands.has_role('league')
async def game_check(ctx, member: discord.Member):
    #check if players have >= 10 games with each other
    cursor.execute(f'SELECT COUNT(DISTINCT id) FROM games WHERE (member_id = {ctx.author.id} AND opponent_id = {member.id}) OR (member_id = {member.id} AND opponent_id = {ctx.author.id});')
    gcount = cursor.fetchone()[0]
    embed = discord.Embed(colour=discord.Colour(0x6790a7))
    embed.add_field(name="Games played", value='{} and {} has played {} games in total.'.format(ctx.author.name, member.name, gcount), inline=True)
    await ctx.send(embed=embed)

# Command shows League Leaderboard from top to bottom
@bot.command(name='top', help=' - show full league leaderbord', aliases=['leaderboard'])
@commands.has_role('league')
async def top(ctx):
    embed = discord.Embed(title="League leaderboard", colour=discord.Colour(0xFFD700))
    # cursor.execute(f'SELECT COUNT(member_id) FROM rating;')
    # pnum = cursor.fetchone()[0]
    n = 0
    for row in cursor.execute(f'SELECT rating,member_name FROM rating ORDER BY rating DESC'):
        n = n + 1
        embed.add_field(name="Position", value=n, inline=True)
        embed.add_field(name="Name", value=row[1], inline=True)
        embed.add_field(name="Rating", value=row[0], inline=True)
    await ctx.send(embed=embed)
    

# Command shows top10 from League Leaderboard
@bot.command(name='top10', help=' - show top 10 league players', aliases=['10'])
@commands.has_role('league')
async def top10(ctx):
    embed = discord.Embed(title="Top 10 League players", colour=discord.Colour(0xFFD700))
    n = 0
    for row in cursor.execute(f'SELECT rating,member_name FROM rating ORDER BY rating DESC LIMIT 10'):
        n = n + 1
        embed.add_field(name="Position", value=n, inline=True)
        embed.add_field(name="Name", value=row[1], inline=True)
        embed.add_field(name="Rating", value=row[0], inline=True)
    await ctx.send(embed=embed)

# command for entering game results, calculaton and updating rating
@bot.command(name='game', help=' - submit opponent\'s result "@opponent win/loss points"')
@commands.has_role('league')
async def results(ctx, member: discord.Member, result, points):
    pt = points
    K = 32        # K-factor

    #check if players have >= 10 games with each other
    cursor.execute(f'SELECT COUNT(DISTINCT id) FROM games WHERE (member_id = {ctx.author.id} AND opponent_id = {member.id}) OR (member_id = {member.id} AND opponent_id = {ctx.author.id});')
    gcount = cursor.fetchone()[0]

    if gcount >= 10:
        embed = discord.Embed(colour=discord.Colour(0xFF0000))
        embed.add_field(name="ERROR", value='{} and {} has reached {} games!'.format(ctx.author.name, member.name, gcount), inline=True)
        await ctx.send(embed=embed)
    else:
    
            # extract current rating for message author
        for a_row in cursor.execute(f'SELECT rating FROM rating WHERE member_id={ctx.author.id}'):
            Ra = a_row[0] # current author rating
    
        # extract current rating for mentioned opponent
        for op_row in cursor.execute(f'SELECT rating FROM rating WHERE member_id={member.id}'):
            Rop = op_row[0] # current opponent rating

        cursor.execute(f'SELECT MAX(id) from games')
        gmax = cursor.fetchone()[0]

        # Update rating as if mentioned opponent won the game
        if result in 'win':
            # calculating ELO
            ## gathered delta points from current game
            Ea = round( 1 / ( 1 + 10 ** ((Rop - Ra) / 400)), 2) # delta for author
            Eop = round( 1 / ( 1 + 10 ** ((Ra - Rop) / 400)), 2) # delta for opponent
    
            ## update rating
            Rna = round( Ra + K * (0 - Ea), 2) # Calculate new Ra as Rna, 0 for loss
            Rnop = round( Rop + K * (1 - Eop), 2) # Calculate new Rop as Rnop, 1 for win
    
            ## Create loss game entry for author
            cursor.execute(f'INSERT INTO games (id,member_id,opponent_id,result,score) VALUES({gmax} + 1,{ctx.author.id},{member.id},"loss","{pt}")')
            conn.commit()
            # update rating and game statistics
            cursor.execute(f'UPDATE rating SET rating = {Rna}, games = games + 1, losses = losses + 1 where member_id={ctx.author.id}')
            conn.commit()
    
            # Create win game entry for opponent
            cursor.execute(f'INSERT INTO games (id,member_id,opponent_id,result,score) VALUES({gmax} + 1,{member.id},{ctx.author.id},"win","{pt}")')
            conn.commit()
            # update rating and game statistics
            cursor.execute(f'UPDATE rating SET rating = {Rnop}, games = games + 1, wins = wins + 1 where member_id={member.id}')
            conn.commit()
    
            msg = await ctx.send(f"{member.name} won with {points}!")
            for reaction in reactions:
                await msg.add_reaction(reaction)
    
            # Pretty output of updated rating for participants
            for row in cursor.execute(f'SELECT rating FROM rating WHERE member_id={ctx.author.id}'):
                embed = discord.Embed(title="Updated League profile", colour=discord.Colour(0x6790a7))
                embed.add_field(name="Delta", value=Ea, inline=True)
                embed.add_field(name="Rating", value=row[0], inline=True)
                embed.set_footer(text=ctx.author.name, icon_url = ctx.author.avatar_url)
                await ctx.send(embed=embed)
            for row in cursor.execute(f'SELECT rating FROM rating WHERE member_id={member.id}'):
                embed = discord.Embed(title="Updated League profile", colour=discord.Colour(0x6790a7))
                embed.add_field(name="Delta", value=Eop, inline=True)
                embed.add_field(name="Rating", value=row[0], inline=True)
                embed.set_footer(text=member.name, icon_url = member.avatar_url)
                await ctx.send(embed=embed)
    
        # Update rating as if mentioned opponent lost the game
        elif result in 'loss':
            ## gathered delta points from current game result
            Ea = round( 1 / (1 + 10 ** ((Rop - Ra) / 400)), 2)
            Eop = round( 1 / (1 + 10 ** ((Ra - Rop) / 400 )), 2)
    
            ## calculate new rating
            Rna = round( Ra + K * (1 - Ea), 2)                    # Calculate new Ra as Rna, 1 for win
            Rnop = round( Rop + K * (0 - Eop), 2)                 # Calculate new Rop as Rnop, 0 for loss
    
            # Create win game entry for message author
            cursor.execute(f'INSERT INTO games (id,member_id,opponent_id,result,score) VALUES({gmax} + 1,{ctx.author.id},{member.id},"win","{pt}")')
            conn.commit()
            # update rating and game statistics
            cursor.execute(f'UPDATE rating SET rating = {Rna}, games = games + 1, wins = wins + 1 where member_id={ctx.author.id}')
            conn.commit()
    
            # Create loss game entry for mentioned opponent
            cursor.execute(f'INSERT INTO games (id,member_id,opponent_id,result,score) VALUES({gmax} + 1,{member.id},{ctx.author.id},"loss","{pt}")')
            conn.commit()
            # update rating and game statistics
            cursor.execute(f'UPDATE rating SET rating = {Rnop}, games = games + 1, losses = losses + 1 where member_id={member.id}')
            conn.commit()
    
            await ctx.send(f'{ctx.author.name} won with {points}!')
    
            # Pretty output of updated rating for participants 
            for row in cursor.execute(f'SELECT rating FROM rating WHERE member_id={ctx.author.id}'):
                embed = discord.Embed(title="Updated League profile", colour=discord.Colour(0x6790a7))
                embed.add_field(name="Delta", value=Ea, inline=True)
                embed.add_field(name="Rating", value=row[0], inline=True)
                embed.set_footer(text=ctx.author.name, icon_url = ctx.author.avatar_url)
                await ctx.send(embed=embed)
            for row in cursor.execute(f'SELECT rating FROM rating WHERE member_id={member.id}'):
                embed = discord.Embed(title="Updated League profile", colour=discord.Colour(0x6790a7))
                embed.add_field(name="Delta", value=Eop, inline=True)
                embed.add_field(name="Rating", value=row[0], inline=True)
                embed.set_footer(text=member.name, icon_url = member.avatar_url)
                await ctx.send(embed=embed)
        else:
            await ctx.send(f'Wrong result!')

# https://www.mmbyte.com/article/95316.html
#
#msg = await ctx.send(embed=embed)
#for reaction in reactions:
#    await msg.add_reaction(reaction)
#
# @bot.event
# async def on_reaction_add(reaction, user):
#     message = reaction.message
#     emoji = reaction.emoji

#     if user.bot:
#         return

#     if emoji == "emoji 1":
#         fixed_channel = bot.get_channel(channel_id)
#         if message.content: await fixed_channel.send(message.content)
#         elif message.embed: await fixed_channel.send(message.embed)
#     elif emoji == "emoji 2":
#         #do stuff
#     elif emoji == "emoji 3":
#         #do stuff
#     else:
#         return

# outpud upon bot connection to the server
@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

bot.run(TOKEN)
# %%