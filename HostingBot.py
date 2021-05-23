    # bot.py
testing = True
import nest_asyncio
nest_asyncio.apply()

import os

from discord.ext import commands
import discord
from dotenv import load_dotenv

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

intents = discord.Intents(messages=True, guilds=True, members = True)

bot = commands.Bot(command_prefix='H!', intents = intents)

import BaW
import Battle
import ORG
import Utils
import Clock
#import Maze
import Coordination
import Autohost
import Music                
#import Control
import Commands
import Comms
import Help
from Functions import botadmin
import random as r
import sys

first = True

logguild = 576830979436445716
logchannelname = 'log'
logchannel = None

songlist = []
songfile = open('songs.txt', 'r')
for i in songfile:
    if i[-1] == '\n':
        songlist.append(i[:-1])
    else:
        songlist.append(i)
songfile.close()
    
def write():
    Commands.write()
    ORG.write()
    Comms.write()
    
async def periodicsave(t, i):
    await nest_asyncio.asyncio.sleep(t)
    # if not logchannel == None:
    #     await logchannel.send('Writing to json...')
    write()
    # if not logchannel == None:
    #     await logchannel.send('Finished writing')
    await periodicsave(t, i)
    
async def report(message):
    if not logchannel == None:
        await logchannel.send(logchannel.guild.owner.mention + ' Report in guild ' + str(message.guild))
        await logchannel.send('Report channel: ' + str(message.channel))
        await logchannel.send('Report author: ' + str(message.author))
        await logchannel.send('Report content: ' + str(message.content))
        await logchannel.send(await message.channel.create_invite(reason='Hosting Bot Report Invite', max_age = 24*3600))
        
async def status(message):
    await message.channel.send('There are ' + str(int(len(BaW.bawplayers)/2)) + ' BaW matches.')
    await message.channel.send('There are ' + str(Battle.numberOfMatches()) + ' Battle matches.')
    await message.channel.send('There are ' + str(len(Clock.clocks)) + ' Clocks.')
    for i in bot.guilds:
        for j in i.channels:
            if j.name.lower().startswith('battle-announcements'):
                print(i.name)
    
async def activeservers(message):
    m = 'Battle Servers:\n'
    battleservers = []
    clockservers = []
    
    for i in list(Battle.BattleDictionary.values()):
        if not i == None and i.active and not i.guild in battleservers:
            battleservers.append(i)
            m += i.guild.name + '\n'
    m += 'Clock Servers:\n'
    for i in list(Clock.clocks):
        if not i.channel.guild in clockservers:
            clockservers.append(i)
            m += i.channel.guild.name + '\n'
    await message.channel.send(m)

@bot.event
async def on_ready():
    await bot.login(token)
    await bot.change_presence(activity = discord.Game(name = "H!Help"))
    global first
    if first:
        first = False
        Commands.setup(bot)
        ORG.setup(bot)
        await Comms.setup(bot)
        for guild in bot.guilds:
            try:
                await Battle.setup(guild)
            except:
                pass
            if guild.id == logguild:
                for channel in guild.channels:
                    if channel.name == logchannelname:
                        global logchannel
                        logchannel = channel
        await periodicsave(3600, 48)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if not testing ^ (message.guild.name == logguild):
        await Battle.onMessage(message)       
        await Coordination.onMessage(message)       

    if message.content.startswith('!'):
        await Commands.Command(message)
    messagearray = None
    if testing:
        if message.content.lower().startswith('z!'):
            if message.content.lower().startswith('z!$'):
                messagearray = ("  " + message.content[3:]).split()
            else:
                messagearray = [i.replace('_', ' ') for i in (" " + message.content[2:]).split()]

    else:
        if message.content.lower().startswith('h!'):
            if message.content.lower().startswith('h!$'):
                messagearray = ("  " + message.content[3:]).split()
            else:
                messagearray = [i.replace('_', ' ') for i in (" " + message.content[2:]).split()]

    if not messagearray == None:
        if messagearray[0].lower() == 'changes':
            m = ''
            m += '5/23/21: Added comms module. This will be tested in Sunvivor season 11-go there for details: https://discord.gg/b6Eh7BmZt5 \n'
            m += 'I also reinstated support for custom commands. In the past I excluded custom commands on the basis that using mainstream discord bots was the better option, but recently said bots have placed limits on custom command usage. Use `H!Help Commands` for details.'
            await message.channel.send(m)
            
        elif messagearray[0].lower() == 'logout' and botadmin(message.author):
                write()
                await bot.logout()
        #elif messagearray[0].lower() == 'testinfo' and botadmin(message.author):#just used for testing when I want random info
        # elif messagearray[0].lower() == 'owners' and botadmin(message.author):#message server owners of servers this bot is in. Have this disabled by default because...duh
        #         ownerlist = []
        #         for i in bot.guilds:
        #             owner = i.owner
        #             if not owner in ownerlist:
        #                 ownerlist.append(owner)
        #                 if botadmin(owner):#for testing stuff, sends only to myself
        #                     channel = owner.dm_channel
        #                     if channel is None:
        #                         channel = await owner.create_dm()
        #                     s = ""
        #                     for i in messagearray[1:]:
        #                         s += i + " "
        #                     await channel.send(s)
                            
        elif messagearray[0].lower() == 'write' and botadmin(message.author): #org commands
            write()
        elif messagearray[0].lower() == 'report':
            await report(message)
            await message.channel.send("Report recorded.")
        elif messagearray[0].lower() == 'status' and botadmin(message.author):#I use this to make sure I don't log out the bot while someone is using it
        #it doesn't show coordination but nobody uses coordination so whatever
            if len(messagearray) == 1:
                await status(message)
            else:
                await activeservers(message)#need this so I can figure out what servers have bot stuff active when I need to shut the bot down
        elif messagearray[0].lower() == 'org': #org commands
            await ORG.ORGRespond(messagearray, message)
        elif messagearray[0].lower() == 'baw': # Black and White
            await BaW.BaWRespond(messagearray, message)
            #nobody uses this anymore :(
            #also the first thing I coded so if you want to see some particularly terrible code go here
        elif messagearray[0].lower() == 'battle': #Dungeon battle
            await Battle.BattleRespond(messagearray, message)
#        elif messagearray[0].lower() == 'maze': #Multi-Dimensional Maze
#            await Maze.MazeRespond(messagearray, message)
#excluded this because I don't think there's interest for it and it can freeze the bot
        elif messagearray[0].lower() == 'coordination':
            await Coordination.CoordinationRespond(messagearray, message)
        elif messagearray[0].lower() == 'comms':
            await Comms.CommsRespond(messagearray, message)
        elif messagearray[0].lower() == 'utils':
            await Utils.UtilsRespond(messagearray, message)
        elif messagearray[0].lower() == 'clock':
            await Clock.ClockRespond(messagearray, message)
        elif messagearray[0].lower() == 'music':
            await Music.MusicRespond(messagearray, message)
        elif messagearray[0].lower() == 'autohost':
            await Autohost.AutohostRespond(messagearray, message)
        # elif messagearray[0].lower() == 'control':
        #         await Control.ControlRespond(messagearray, message)
        #this only works when the program is running on a computer, so no point in including it
        elif messagearray[0].lower() == 'link':
            await message.channel.send('https://discordapp.com/api/oauth2/authorize?client_id=624103123639730176&permissions=8&scope=bot')
        elif messagearray[0].lower() == 'help':
            await Help.HelpRespond(messagearray, message)
        elif messagearray[0].lower() == 'commands' and message.author.guild_permissions.administrator:
            await Commands.CommandsRespond(messagearray, message)
    #Custom commands system like other bots (dyno) have. Not really any point in having it active.
        elif messagearray[0].lower() == 'echo' and message.author.guild_permissions.administrator:
            s = ""
            for i in messagearray[1:]:
                s += i + " "
            await message.channel.send(s)
        elif messagearray[0].lower() == 'channelecho' and message.author.guild_permissions.administrator:
            cha=None
            for i in message.guild.channels:
                if i.name == messagearray[1]:
                    cha = i
            if cha==None:
                return
            s = ""
            for i in messagearray[2:]:
                s += i + " "
            await cha.send(s)
        elif messagearray[0].lower() == 'guildecho' and botadmin(message.author):
            gu = None
            for i in bot.guilds:
                if i.name == messagearray[1]:
                    gu = i
            if gu == None:
                return
            cha=None
            for i in gu.channels:
                if i.name == messagearray[2]:
                    cha = i
            if cha==None:
                return
            s = ""
            for i in messagearray[3:]:
                s += i + " "
            await cha.send(s)
        elif messagearray[0].lower() == 'banger':
            await message.channel.send('https://www.youtube.com/watch?v=' + r.choice(songlist))
        elif messagearray[0].lower() == 'addsong':
            song = messagearray[1][-11:]
            if song in songlist:
                await message.channel.send('That song is already in the list.')
            elif botadmin(message.author):
                songlist.append(song)
                songfile = open('songs.txt', 'a')
                songfile.write('\n' + song)
                songfile.close()
            else:
                await logchannel.send('https://www.youtube.com/watch?v=' + song)
                
# @bot.event
# async def on_error(event, *args, **kwargs):
#     message = args[0]
#     await message.channel.send("There was an error.")
#     info = sys.exc_info()
#     print(info)
#     print(info[0])
#     print(info[1])
#     tb = info[2]
#     print(tb)
#     print(tb.tb_frame)
#     print(tb.tb_lineno)
#     print(tb.tb_lasti)
#     print('Error in server ' + message.guild.name)
#     print(str(event))
#     print(str(args))
#     print(str(kwargs))
                
@bot.event
async def on_guild_join(guild):
    ORG.addGuild(guild)
    Commands.addGuild(guild)
    await Battle.setup(guild)
@bot.event
async def on_guild_remove(guild):
    ORG.removeGuild(guild)
    
bot.run(token)