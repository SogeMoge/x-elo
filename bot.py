# bot.py
import os
import random
import discord

#load sensitive data from .env file
from dotenv import load_dotenv

from discord.ext import commands
from discord.utils import get

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='%', intents=intents)

# load token from .env file
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
INFO_CH_ID = int(os.getenv('INFO_CHANNEL_ID'))
BOT_ID = int(os.getenv('BOT_USER_ID'))

client = discord.Client()



import logging
logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# set prefix for bot commands
#bot = commands.Bot(command_prefix='%')


# open connection to database
import sqlite3
conn = sqlite3.connect(os.getenv('DB'))
cursor = conn.cursor()
# conn.close()  # close database connection

reactions = ['\U00002705','\U0000274e'] # check and cross marks
update_reaction = '\U0001f504' # circle arrows

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
            await ctx.send(f"League account created")
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
    cursor.execute(f'SELECT COUNT(member_name) FROM rating WHERE rating >= (SELECT rating FROM rating WHERE member_id={ctx.author.id})')
    pos = cursor.fetchone()[0]
    for row in cursor.execute(f'SELECT rating,games,wins,losses FROM rating WHERE member_id={ctx.author.id}'):
        embed = discord.Embed(title="League profile", colour=discord.Colour(0xFFD700))
        embed.add_field(name="Position", value=pos, inline=False)
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
    cursor.execute(f'SELECT COUNT(DISTINCT id) FROM games WHERE id != 0 AND ((member_id = {ctx.author.id} AND opponent_id = {member.id}) OR (member_id = {member.id} AND opponent_id = {ctx.author.id}));')
    gcount = cursor.fetchone()[0]
    embed = discord.Embed(colour=discord.Colour(0x6790a7))
    embed.add_field(name="Games played", value='{} and {} have played {} games in total, not including tournament games.'.format(ctx.author.name, member.name, gcount), inline=True)
    await ctx.send(embed=embed)

# Command shows League Leaderboard from top to bottom
@bot.command(name='top', help=' - show full league leaderbord', aliases=['leaderboard'])
@commands.has_role('league admin')
async def top(ctx):
    embed = discord.Embed(title="League leaderboard", colour=discord.Colour(0xFFD700))
    # cursor.execute(f'SELECT COUNT(member_id) FROM rating;')
    # pnum = cursor.fetchone()[0]
    n = 0
    for row in cursor.execute(f'SELECT rating||" - "||member_name||", W:"||wins||" L:"||losses FROM rating WHERE games >= 1 ORDER BY rating DESC, games DESC;'):
        n = n + 1
        # embed.add_field(name="№", value=n, inline=False)
        embed.add_field(name="\u200b", value='{} - {}'.format(n, row[0]), inline=False)
    # await ctx.send(embed=embed)
    top = await ctx.send(embed=embed)
    await top.add_reaction(update_reaction)

@bot.event
async def on_raw_reaction_add(payload):
    user = payload.user_id
    emoji = payload.emoji
    if user == BOT_ID:
        return
    else:
        if payload.emoji.name == update_reaction:
            fixed_channel = bot.get_channel(INFO_CH_ID) #channel where the command will work
            user = bot.get_user(payload.user_id)
            msg = await fixed_channel.fetch_message(payload.message_id)
            await msg.remove_reaction(emoji, user)
            await msg.delete()
            # embed = msg.embeds[0]
            # await fixed_channel.send(embed=embed)

            embed = discord.Embed(title="League leaderboard", colour=discord.Colour(0xFFD700))
            n = 0
            for row in cursor.execute(f'SELECT rating||" - "||member_name||", W:"||wins||" L:"||losses FROM rating WHERE games >= 1 ORDER BY rating DESC, games DESC;'):
                n = n + 1
                # embed.add_field(name="№", value=n, inline=True)
                embed.add_field(name="\u200b", value='{} - {}'.format(n, row[0]), inline=False)
            top = await fixed_channel.send(embed=embed)
            await top.add_reaction(update_reaction)

# Command shows top10 from League Leaderboard
# @bot.command(name='top10', help=' - show top 10 league players', aliases=['10'])
# @commands.has_role('league admin')
# async def top10(ctx):
#     embed = discord.Embed(title="Top 10 League players", colour=discord.Colour(0xFFD700))
#     n = 0
#     for row in cursor.execute(f'SELECT rating,member_name FROM rating ORDER BY rating DESC LIMIT 10'):
#         n = n + 1
#         embed.add_field(name="Position", value=n, inline=True)
#         embed.add_field(name="Name", value=row[1], inline=True)
#         embed.add_field(name="Rating", value=row[0], inline=True)
#     await ctx.send(embed=embed)

# command for entering tournament paring results between league members

@bot.command(name='tgame', help=' - sumbit tournament result "@winner win @looser loss points"')
@commands.has_role('league admin')
async def tresults(ctx, member1: discord.Member, result1, member2: discord.Member, result2, points):
    if ctx.channel.name != 'запись-результатов':
        embed = discord.Embed(colour=discord.Colour(0xFF0000))
        embed.add_field(name="ERROR", value='Wrong channel!', inline=True)
        await ctx.send(embed=embed)
        return
    elif result1 not in 'win':
        embed = discord.Embed(colour=discord.Colour(0xFF0000))
        embed.add_field(name="ERROR", value='First opponent have to be a winner, followed by "win"', inline=True)
        await ctx.send(embed=embed)
        return
    elif result2 not in 'loss':
        embed = discord.Embed(colour=discord.Colour(0xFF0000))
        embed.add_field(name="ERROR", value='First opponent have to be a looser, followed by "loss"', inline=True)
        await ctx.send(embed=embed)
        return
    pt = points
    K = 32
    # extract current rating for message winner
    for a_row in cursor.execute(f'SELECT rating FROM rating WHERE member_id={member1.id}'):
        Ra = a_row[0] # winner rating
    # extract current rating for mentioned looser
    for op_row in cursor.execute(f'SELECT rating FROM rating WHERE member_id={member2.id}'):
        Rop = op_row[0] # looser rating
    # all tournaments games will be inserted with number 0
    gtourney = 0
    # calculating ELO
    ## gathered delta points from current game result
    Ea = round( 1 / (1 + 10 ** ((Rop - Ra) / 400)), 2)
    Eop = round( 1 / (1 + 10 ** ((Ra - Rop) / 400 )), 2)
    ## calculate new rating
    Rna = round( Ra + K * (1 - Ea), 2)                    # Calculate new Ra as Rna, 1 for win
    Rna_diff = round(Rna - Ra, 2) 
    Rnop = round( Rop + K * (0 - Eop), 2)                 # Calculate new Rop as Rnop, 0 for loss
    Rnop_diff = round(Rop - Rnop, 2)
    # Create win game entry for message author
    cursor.execute(f'INSERT INTO games (id,member_id,opponent_id,result,score) VALUES({gtourney},{member1.id},{member2.id},"win","{pt}")')
    conn.commit()
    # update rating and game statistics
    cursor.execute(f'UPDATE rating SET rating = {Rna}, games = games + 1, wins = wins + 1 where member_id={member1.id}')
    conn.commit()
    # Create loss game entry for mentioned opponent
    cursor.execute(f'INSERT INTO games (id,member_id,opponent_id,result,score) VALUES({gtourney},{member2.id},{member1.id},"loss","{pt}")')
    conn.commit()
    # update rating and game statistics
    cursor.execute(f'UPDATE rating SET rating = {Rnop}, games = games + 1, losses = losses + 1 where member_id={member2.id}')
    conn.commit()
    msg = await ctx.send(f'{member1.name} won in a tournament match with {member2.name},  {points}!')
    # add confirmation reactions to game results message
    for reaction in reactions:
        await msg.add_reaction(reaction)
    # Pretty output of updated rating for participants 
    for row in cursor.execute(f'SELECT rating FROM rating WHERE member_id={member1.id}'):
        embed = discord.Embed(title="Updated League profile", colour=discord.Colour(0x6790a7))
        embed.add_field(name="Diff", value=Rna_diff, inline=True)
        embed.add_field(name="Rating", value=row[0], inline=True)
        embed.set_footer(text=member1.name, icon_url = member1.avatar_url)
        await ctx.send(embed=embed)
    for row in cursor.execute(f'SELECT rating FROM rating WHERE member_id={member2.id}'):
        embed = discord.Embed(title="Updated League profile", colour=discord.Colour(0x6790a7))
        embed.add_field(name="Diff", value=Rnop_diff, inline=True)
        embed.add_field(name="Rating", value=row[0], inline=True)
        embed.set_footer(text=member2.name, icon_url = member2.avatar_url)
        await ctx.send(embed=embed)



# command for entering game results, calculaton and updating rating
@bot.command(name='game', help=' - submit opponent\'s result "@opponent win/loss points"')
@commands.has_role('league')
async def results(ctx, member: discord.Member, result, points):
    role_check = discord.utils.get(ctx.guild.roles, name="league")  
    if ctx.channel.name != 'запись-результатов':
        embed = discord.Embed(colour=discord.Colour(0xFF0000))
        embed.add_field(name="ERROR", value='Wrong channel!', inline=True)
        await ctx.send(embed=embed)
        return
    elif role_check not in member.roles:
        embed = discord.Embed(colour=discord.Colour(0xFF0000))
        embed.add_field(name="ERROR", value='{} is not a league member!'.format(member.name), inline=True)
        await ctx.send(embed=embed)
        return
    elif ctx.author.id == member.id:
        embed = discord.Embed(colour=discord.Colour(0xFF0000))
        embed.add_field(name="ERROR", value='You can not play with yourself!', inline=True)
        await ctx.send(embed=embed)
        return
    pt = points
    K = 32        # K-factor

    #check if players have >= 10 games with each other
    cursor.execute(f'SELECT COUNT(DISTINCT id) FROM games WHERE id != 0 AND ((member_id = {ctx.author.id} AND opponent_id = {member.id}) OR (member_id = {member.id} AND opponent_id = {ctx.author.id}));')
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

        cursor.execute(f'SELECT COALESCE(MAX(id), 0) from games')
        gmax = cursor.fetchone()[0]

        # Update rating as if mentioned opponent won the game
        if result in 'win':
            # calculating ELO
            ## gathered delta points from current game
            Ea = round( 1 / ( 1 + 10 ** ((Rop - Ra) / 400)), 2) # delta for author
            Eop = round( 1 / ( 1 + 10 ** ((Ra - Rop) / 400)), 2) # delta for opponent
    
            ## update rating
            Rna = round( Ra + K * (0 - Ea), 2) # Calculate new Ra as Rna, 0 for loss
            Rna_diff = round(Ra - Rna, 2)
            Rnop = round( Rop + K * (1 - Eop), 2) # Calculate new Rop as Rnop, 1 for win
            Rnop_diff = round(Rnop - Rop, 2)
    
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
            # add confirmation reactions to game results message
            for reaction in reactions:
                await msg.add_reaction(reaction)
    
            # Pretty output of updated rating for participants
            for row in cursor.execute(f'SELECT rating FROM rating WHERE member_id={ctx.author.id}'):
                embed = discord.Embed(title="Updated League profile", colour=discord.Colour(0x6790a7))
                embed.add_field(name="Diff", value=Rna_diff, inline=True)
                embed.add_field(name="Rating", value=row[0], inline=True)
                embed.set_footer(text=ctx.author.name, icon_url = ctx.author.avatar_url)
                await ctx.send(embed=embed)
            for row in cursor.execute(f'SELECT rating FROM rating WHERE member_id={member.id}'):
                embed = discord.Embed(title="Updated League profile", colour=discord.Colour(0x6790a7))
                embed.add_field(name="Diff", value=Rnop_diff, inline=True)
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
            Rna_diff = round(Rna - Ra, 2) 
            Rnop = round( Rop + K * (0 - Eop), 2)                 # Calculate new Rop as Rnop, 0 for loss
            Rnop_diff = round(Rop - Rnop, 2)
    
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
    
            msg = await ctx.send(f'{ctx.author.name} won with {points}!')
            # add confirmation reactions to game results message
            for reaction in reactions:
                await msg.add_reaction(reaction)
    
            # Pretty output of updated rating for participants 
            for row in cursor.execute(f'SELECT rating FROM rating WHERE member_id={ctx.author.id}'):
                embed = discord.Embed(title="Updated League profile", colour=discord.Colour(0x6790a7))
                embed.add_field(name="Diff", value=Rna_diff, inline=True)
                embed.add_field(name="Rating", value=row[0], inline=True)
                embed.set_footer(text=ctx.author.name, icon_url = ctx.author.avatar_url)
                await ctx.send(embed=embed)
            for row in cursor.execute(f'SELECT rating FROM rating WHERE member_id={member.id}'):
                embed = discord.Embed(title="Updated League profile", colour=discord.Colour(0x6790a7))
                embed.add_field(name="Diff", value=Rnop_diff, inline=True)
                embed.add_field(name="Rating", value=row[0], inline=True)
                embed.set_footer(text=member.name, icon_url = member.avatar_url)
                await ctx.send(embed=embed)
        else:
            await ctx.send(f'Wrong result!')

# outpud upon bot connection to the server
@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

bot.run(TOKEN)
# %%
