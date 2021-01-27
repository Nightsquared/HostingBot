import random
import discord
from Functions import botadmin
async def setPerms(message, role, overwrites):
    await message.channel.set_permissions(role, overwrite = overwrites)
    
async def UtilsRespond(messagearray, message):
    if messagearray[1].lower() == 'ping':
        await message.channel.send("Response")
        
    if messagearray[1].lower() == 'choose':
        await message.channel.send(random.choice(messagearray[2:]))
    
    if messagearray[1].lower() == 'channels' and message.author.guild_permissions.administrator:
        await message.channel.send(str(len(message.guild.channels)))
        
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