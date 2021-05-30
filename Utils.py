import random
import discord
from Functions import botadmin
import datetime

async def setPerms(message, role, overwrites):
    await message.channel.set_permissions(role, overwrite = overwrites)
    
async def UtilsRespond(messagearray, message):
    if messagearray[1].lower() == 'ping':
        await message.channel.send(message.created_at-datetime.datetime.now())
        #await message.channel.send("Response")
        
    if messagearray[1].lower() == 'choose':
        await message.channel.send(random.choice(messagearray[2:]))
    
    if messagearray[1].lower() == 'channels' and message.author.guild_permissions.administrator:
        await message.channel.send(str(len(message.guild.channels)))
        
    if messagearray[1].lower() == 'move' and message.author.guild_permissions.administrator:
        if messagearray[2] is None:
            await message.channel.send('Invalid. First argument is the Category')
        else:
            category = discord.utils.get(message.guild.channels, name=messagearray[2])
            await message.channel.edit(category=category)
        
    if messagearray[1].lower() == 'perm' and message.author.guild_permissions.administrator:
        if messagearray[2].lower() == 'read':
            for i in messagearray[3:]:
                await setPerms(message, discord.utils.get(message.guild.roles, name=i), discord.PermissionOverwrite(read_messages = True, send_messages = False, read_message_history=True))
        
        if messagearray[2].lower() == 'write':
            for i in messagearray[3:]:
                await setPerms(message, discord.utils.get(message.guild.roles, name=i), discord.PermissionOverwrite(read_messages = True, send_messages = True, read_message_history=True))
                
        if messagearray[2].lower() == 'hide':
            for i in messagearray[3:]:
                await setPerms(message, discord.utils.get(message.guild.roles, name=i), discord.PermissionOverwrite(read_messages = False, send_messages = False, read_message_history=False))
                
        if messagearray[2].lower() == 'remove':
            for i in messagearray[3:]:
                await setPerms(message, discord.utils.get(message.guild.roles, name=i), None)
    
    if messagearray[1].lower() == 'equilibrium':
            try:
                num = int(messagearray[2])
            except:
                num = 4
            s1 = 'First set: '
            s2 = 'Second set: '
            choices = list(range(1, 11))
            for i in range(num):
                n1 = random.choice(choices)
                n2 = random.choice(choices)
                s1 += str(n1) + ', '
                s2 += str(n2) + ', '
            s1 = s1[:-2] + '\n'
            s2 = s2[:-2]
            await message.channel.send(s1 + s2)
            
    if messagearray[1].lower() == 'numberset':
            try:
                num = int(messagearray[2])
            except:
                num = 4
            s1 = ''
            choices = list(range(0, 11))
            for i in range(num):
                n1 = random.choice(choices)
                s1 += str(n1) + ', '
            s1 = s1[:-2]
            await message.channel.send(s1)
    
    if messagearray[1].lower() == 'countcheck' and message.author.guild_permissions.administrator:
        messagelist = []
        roles = [i for i in message.role_mentions]
        users = []
        for role in roles:
            for user in role.members:
                if not user in users:
                    users.append(user)
        counter = 0
        async for message2 in message.channel.history(limit=None, oldest_first=True):
            if users == [] or message2.author in users:
                try:
                    a = int(message2.content)
                    if not a == counter + 1:
                        messagelist.append(await message2.reply('Number of interest', mention_author=False))
                    counter = a
                except:
                    #pass
                    #print(message.author)
                    #try:
                    if not message2 in messagelist and not message2 == message:
                        messagelist.append(await message2.reply('Message of interest', mention_author=False))
                    #except:
                        #pass
                        
        await message.channel.send('Finished.')
                
    if messagearray[1].lower() == 'count' and message.author.guild_permissions.administrator:
        if len(messagearray) == 3:
            start = 1
            try:
                end = int(messagearray[2])
            except:
                pass
        else:
            try:
                start = int(messagearray[2])
            except:
                pass
            try:
                end = int(messagearray[3])
            except:
                pass
        for i in range(start, end+1):
            await message.channel.send(str(i))

    if messagearray[1].lower() == 'error':
        assert 1 == 0
                