import json
import discord
from Functions import botadmin
messagedict = {}
def setup(bot):
    for guild in bot.guilds:
        messagedict.update({str(guild.id):{}})
    messagefile = open('messages.json', 'r')
    try:
        messagedict.update(json.load(messagefile))
        messagefile.close()
    except:
        messagefile.close()
        
def addGuild(Guild):
    messagedict.update({str(Guild.id):{}})
    
def removeGuild(Guild):
    return messagedict.pop(str(Guild.id))

async def CommandsRespond(messagearray, message):
    guildID = str(message.guild.id)
    if messagearray[1].lower() == 'add':
        s = ""
        for i in messagearray[3:]:
            s += i.replace('\\n', '\n') + " "
        messagedict[guildID].update({messagearray[2]:s})
    elif messagearray[1].lower() == 'list':
        m = ''
        for i in messagedict[guildID].keys():
            m += '!' + i + '\n'
        if m == '':
            m = 'No custom commands'
        await message.channel.send(m)
    elif messagearray[1].lower() == 'remove':
        for i in messagearray[2:]:
            del messagedict[guildID][i]
    elif messagearray[1].lower() == 'write' and botadmin(message.author):
        write()
async def Command(message):
    mc = message.content.split()[0][1:]
    guildID = str(message.guild.id)
    if mc in messagedict[guildID].keys():
        await message.channel.send(messagedict[guildID][mc])

def write():
    messagefile = open('messages.json', 'w')
    json.dump(messagedict, messagefile)
    messagefile.close()