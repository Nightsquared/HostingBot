import nest_asyncio as sy
import discord
import time as t
import Clock
import json

dictionary = {}

class User:
    def __init__(self, user, settings):
        self.user = user
        self.settings = settings
        self.defaulttime = settings.defaulttime
        self.timeremaining = self.defaulttime
        self.lastchecktime = None #absolute time of the last occasion when time was deducted from this user. 
        self.active = False #whether time is running and the user can send messages or not
        self.timemessage = None #the message telling the user how much time they have remaining. This message is generated whenever the user activates their time, and is set to None when they deactivate their time. Well, hopefully anyways
        self.ticktime = 5 #how many seconds between ticks (when the bot deducts the time passed from the user's time).
        self.timedeductedonactivation = settings.timedeductedonactivation
        
    def reset(self):
        self.timeremaining = self.defaulttime
        
    async def tick(self):
        if self.active:
            thistime = t.time()
            self.timeremaining -= thistime - self.lastchecktime
            self.lastchecktime = thistime
            if self.timeremaining <= 0:
                #stop
                await self.deactivate()
                await self.timemessage.edit(content = "You ran out of time.")
            await self.timemessage.edit(content = "Time remaining: " + Clock.time(int(self.timeremaining)))
            return True
        return False
            
        
    async def activate(self, message):
        if self.timeremaining <= self.timedeductedonactivation:
            await message.channel.send('You don\'t have enough time left to activate comms.')
            return
        self.timeremaining -= self.timedeductedonactivation
        self.active = True
        self.lastchecktime = t.time()
        channels = await self.settings.guild.fetch_channels()
        for i in channels:
            if i.permissions_for(self.user).read_messages and not i.category_id in self.settings.exemptcategories: #any channel the player can read will be set so that they can write in it. This should be tested more to make sure they don't somehow gain access to channels they can't actually read.
            #use exemptions to make sure they can't write in treemail or whatever.
                await i.set_permissions(self.user, overwrite = discord.PermissionOverwrite(read_messages = True, send_messages = True, read_message_history=True, add_reactions = True))
        self.timemessage = await message.channel.send("Time remaining: " + Clock.time(int(self.timeremaining)))
        while self.active:
            await sy.asyncio.sleep(self.ticktime)
            await self.tick()
            
    async def deactivate(self):
        self.active = False
        thistime = t.time()
        try:
            self.timeremaining -= thistime - self.lastchecktime
        except:
            pass
        self.lastchecktime = thistime
        channels = await self.settings.guild.fetch_channels()
        if not self.timemessage == None:
            await self.timemessage.edit(content = "Time remaining: " + Clock.time(int(self.timeremaining)))
        for i in channels:
            if i.permissions_for(self.user).send_messages and not i.category_id in self.settings.exemptcategories: #any channel the player can write in will be set so they can't write in it.
                await i.set_permissions(self.user, overwrite = discord.PermissionOverwrite(read_messages = True, send_messages = False, read_message_history=True, add_reactions = False))
                
class Settings:#named this settings. It's more like a guild information object, but I thought it would be confusingly redundant to call it server or something.
    def __init__(self, guild, defaulttime = 120*60, refreshtime = None, exemptcategories = [], timedeductedonactivation = 30):
        self.guild = guild
        self.defaulttime = defaulttime #2 hours by default
        self.users = {}
        self.exemptcategories = exemptcategories#categories that will not have permissions changed. i.e. tribe categories, official stuff, ect.
        self.refreshtime = refreshtime
        self.autorefreshnum = 0
        self.refreshannouncementchannel = None
        self.timedeductedonactivation = timedeductedonactivation
        
    async def autorefresh(self, num):
        while num == self.autorefreshnum:#if the autorefresh command is entered again or something else relevant happens, increasing the autorefreshnum should stop the process
            await sy.asyncio.sleep(self.refreshtime)
            if num == self.autorefreshnum:
                await self.refresh()
            else:
                return
    
    async def refresh(self):
        for i in self.users.values():
            i.reset()
        if not self.refreshannouncementchannel == None:
            await self.refreshannouncementchannel.send("Times have been refreshed!") #see autorefresh command
            
    def jsondict(self):
        d = {'guildID':self.guild.id, 'defaulttime':self.defaulttime, 'users':[(i.user.id, i.timeremaining) for i in list(self.users.values())], 'exemptcategories':self.exemptcategories, 'refreshtime': self.refreshtime, 'timedeductedonactivation': self.timedeductedonactivation}
        if not self.refreshannouncementchannel == None:
            d.update({'refreshannouncementchannel':self.refreshannouncementchannel.id})
        else:
            d.update({'refreshannouncementchannel':None})
        return d
         
    async def registerUser(self, user):
        if user == None:
            return None
        for i in list(self.users.values()):
            if user == i.user:
                return None
        userobject = User(user, self)
        self.users.update({user.id:userobject})
        await userobject.deactivate() #when a user is registered they will lose writing access in nonexempt channels.
        return userobject
        
def write():
    file = open('comms.json', 'w')
    orgsdict = {k:dictionary[k].jsondict() for k in dictionary.keys()}
    json.dump(orgsdict, file)
    file.close()
    
def checkUser(user, guild):
    try:
        return dictionary[guild.id].users[user.id].active
    except:
        return None

async def setup(bot):
    file = open('comms.json', 'r')
    tempdict = json.load(file)
    for guild in bot.guilds:
        if str(guild.id) in list(tempdict.keys()):
            thisdict = tempdict[str(guild.id)]
            settings = Settings(guild, thisdict['defaulttime'], thisdict['refreshtime'], thisdict['exemptcategories'], thisdict['timedeductedonactivation'])
            for userinfo in thisdict['users']:
                for member in guild.members:
                    if member.id == userinfo[0]:
                        user = await settings.registerUser(member)
                        user.timeremaining = userinfo[1]
            # for channelid in thisdict['exemptcategories']:
            #     for channel in guild.channels:
            #         if channel.id == channelid:
            #             settings.exemptcategories.append(channel)
            if not thisdict['refreshannouncementchannel'] == None:
                for channel in guild.channels:
                    if channel.id == thisdict['refreshannouncementchannel']:
                        settings.refreshannouncementchannel = channel
                        #await channel.send('The bot has been reset. Auto-refreshing will need to be re-enabled.')
            
            dictionary.update({guild.id:settings})
    
async def CommsRespond(messagearray, message):
    global dictionary
    
    # Host commands
    if messagearray[1].lower() == 'serverregister' and message.author.guild_permissions.administrator: #registers a server, argument is the default time each player will have. Once settings and stuff are saved to a file some kind of loading should be done instead (there will probably be autoloading)
        try:
            time = float(messagearray[2])
        except:
            time = 120*60
        dictionary.update({message.guild.id:Settings(message.guild, time)})
        await message.channel.send('Server registered.')
    
    if messagearray[1].lower() == 'settings':
        if not message.guild.id in dictionary.keys():
            await message.channel.send("You don't appear to have registered the server.")
        elif message.author.guild_permissions.administrator:
            outmessage = ''
            settings = dictionary[message.guild.id]
            outmessage += 'Default time: ' + str(settings.defaulttime) + '\n'
            outmessage += 'Exempt categories:\n'
            for exempt in settings.exemptcategories:
                if len(outmessage) > 1500:
                    await message.channel.send(outmessage)
                    outmessage = ''
                outmessage += '  ' + discord.utils.get(settings.guild.channels, id=exempt).name + '\n'
            outmessage += 'Time deducted on activation: ' + str(settings.timedeductedonactivation) + '\n'
            outmessage += 'Refresh time: ' + str(settings.refreshtime) + '\n'
            outmessage += 'Refresh announcement channel: ' + str(settings.refreshannouncementchannel) + '\n'
            outmessage += 'Users:\n'
            for user in settings.users.values():
                if len(outmessage) > 1500:
                    await message.channel.send(outmessage)
                    outmessage = ''
                outmessage += '  ' + user.user.display_name + ': \n'
                outmessage += '    Time remaining: ' + str(user.timeremaining) + '\n'
                outmessage += '    Active: ' + str(user.active) + '\n'
            await message.channel.send(outmessage)
            
    if messagearray[1].lower() == 'setdeduction':
        if not message.guild.id in dictionary.keys():
            await message.channel.send("You don't appear to have registered the server.")
        elif message.author.guild_permissions.administrator:
            settings = dictionary[message.guild.id]
            try:
                settings.timedeductiononactivation = int(messagearray[2])
            except:
                await message.channel.send('The first argument needs to be an integer')
                return
            for user in settings.users.values():
                user.timedeductiononactivation = settings.timedeductiononactivation
            await message.channel.send('Time deduction changed.')
        
    if messagearray[1].lower() == 'setdefaulttime':
        if not message.guild.id in dictionary.keys():
            await message.channel.send("You don't appear to have registered the server.")
        elif message.author.guild_permissions.administrator:
            settings = dictionary[message.guild.id]
            try:
                settings.defaulttime = int(messagearray[2])
            except:
                await message.channel.send('The first argument needs to be an integer')
                return
            for user in settings.users.values():
                user.defaulttime = settings.defaulttime
            await message.channel.send('Default time changed.')
        
    if messagearray[1].lower() == 'register' and message.author.guild_permissions.administrator: #registers mentioned players. Server must be registered first.
        if not message.guild.id in dictionary.keys():
            await message.channel.send("You don't appear to have registered the server.")
        else:
            for i in message.mentions:
                await dictionary[message.guild.id].registerUser(i)
    
    if messagearray[1].lower() == 'addtime' and message.author.guild_permissions.administrator: #self explanatory. Negative values will remove time.
        if not message.guild.id in dictionary.keys():
            await message.channel.send("You don't appear to have registered the server.")
        else:
            settings = dictionary[message.guild.id]
            try:
                timeadd = int(messagearray[2])
            except:
                message.channel.send('The first argument needs to be a number.')
                return
            for i in message.mentions:
                try:
                    settings.users[i.id].timeremaining += timeadd
                except:
                    message.channel.send('Had a problem adding time for ' + i.name + '. They might not be registerd.')
                    
    if messagearray[1].lower() == 'settime' and message.author.guild_permissions.administrator: #set time for users. Basically the same command as above but with the + preceding the = removed
        if not message.guild.id in dictionary.keys():
            await message.channel.send("You don't appear to have registered the server.")
        else:
            settings = dictionary[message.guild.id]
            try:
                timeadd = int(messagearray[2])
                assert timeadd >= 0
            except:
                message.channel.send('The first argument needs to be a number that is greater than or equal to 0.')
                return
            for i in message.mentions:
                try:
                    settings.users[i.id].timeremaining = timeadd
                except:
                    message.channel.send('Had a problem setting time for ' + i.name + '. They might not be registerd.')            
        
    if messagearray[1].lower() == 'exempt' and message.author.guild_permissions.administrator:
        if not message.guild.id in dictionary.keys():
            await message.channel.send("You don't appear to have registered the server.")
            return
        if message.channel.category_id in dictionary[message.guild.id].exemptcategories:
            dictionary[message.guild.id].exemptcategories.remove(message.channel.category_id)
            await message.channel.send("Category removed from exemptions.")
        else:
            dictionary[message.guild.id].exemptcategories.append(message.channel.category_id)
            await message.channel.send("Category added to exemptions.")
    
    if messagearray[1].lower() == 'autorefresh' and message.author.guild_permissions.administrator: #the one argument for this is the time between refreshes
        settings = dictionary[message.guild.id]
        if settings.refreshtime == None:
            try:
                time = float(messagearray[2])
            except:
                time = 60*60*24 #24 hours by default
            settings.refreshtime = time
            settings.refreshannouncementchannel = message.channel #bot will automatically announce that time has been replenished in the channel the autorefresh command was sent in (by default) 
            settings.autorefreshnum += 1
            await message.channel.send("Autorefresh activated")
            await settings.autorefresh(int(settings.autorefreshnum))
        else:
            settings.autorefreshnum += 1
            settings.refreshtime = None
            await message.channel.send("Autorefresh cancelled")
            
    if messagearray[1].lower() == 'refresh' and message.author.guild_permissions.administrator:
        await dictionary[message.guild.id].refresh()
        
    # Player commands
    if messagearray[1].lower() == 'activate':
        await dictionary[message.guild.id].users[message.author.id].activate(message)
        
    if messagearray[1].lower() == 'deactivate':
        await dictionary[message.guild.id].users[message.author.id].deactivate()
        await message.channel.send('Comms deactivated.')