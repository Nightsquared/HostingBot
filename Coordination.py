import discord
import random
from Functions import botadmin
import nest_asyncio as sy
#import csv
import Clock
import math
CoordinationDictionary = {}

class Coordination:
    def __init__(self, guild, areas, participant, spectators):
        self.areas = [Area(i, self) for i in range(areas)]
        self.participant = participant
        self.spectators = spectators #list of roles
        self.guild = guild
        self.tasks = []
        self.active = True
        self.difficulty = 10
        self.timenumerator = 100
        
    async def channelSetup(self):
        self.category = await self.guild.create_category("Coordination")
        Perms = {}
        Perms.update({self.participant:discord.PermissionOverwrite(read_messages = True, send_messages = True, read_message_history=True)})
        for role in self.spectators:
            Perms.update({role:discord.PermissionOverwrite(read_messages = True, send_messages = False, read_message_history=True)})
        Perms.update({self.guild.default_role:discord.PermissionOverwrite(read_messages=False)})
        self.announcementschannel = await self.guild.create_text_channel('Tasks', overwrites=Perms, category=self.category)
        for area in self.areas:
            area.channel = await self.guild.create_text_channel(area.name, overwrites=Perms, category=self.category)
        
    async def start(self):
        while self.active:
            Task(self)
            sy.asyncio.create_task(self.tasks[-1].activate())
            await sy.asyncio.sleep(max((self.timenumerator / math.pow((self.difficulty - 2), .9))*(random.random()/4+.875), .25))
            self.difficulty += 1
        await self.endtasks()
            
    async def finish(self):
        if self.active:
            await self.announcementschannel.send('You reached level ' + str(self.difficulty) + '.')
        self.active = False
                
    async def endtasks(self):
        for i in self.tasks:
            try:
                await i.completed()
            except:
                pass

class Area:
    def __init__(self, n, coordination):
        self.name = 'Area ' + str(n)
        self.tasks = []
        self.channel = None
        self.coordination = coordination
        
class Task:
    letterlist = [chr(ord('a')+i) for i in range(26)]
    def __init__(self, coordination):
        self.coordination = coordination
        self.letters = ''
        for i in range(int(math.log(self.coordination.difficulty-5, 4) + random.random())):
            self.letters += random.choice(Task.letterlist)
        self.area = random.choice(self.coordination.areas)
        self.area.tasks.append(self)
        self.coordination.tasks.append(self)
        self.done = False
    
    async def activate(self):
        self.time = max(int((120*math.pow(.5, (math.log(self.coordination.difficulty, 2) - math.log(5, 2))) - 1)*(random.random()/4+.875)), 1)
        self.clock = Clock.AppClock(self.time, self.coordination.announcementschannel, 'You have {time} seconds left for this task.', donemessage = False, pin = False)
        self.clock.ticktime = 1
        Clock.clocks.append(self.clock)
        s = ''
        for i in self.letters:
            s += i + '-'
        s = s[:-1]
        self.message = await self.coordination.announcementschannel.send('Enter ' + s + ' in ' + self.area.name + '.')
        await Clock.clocks[-1].start()
        if not self.done:
            await self.coordination.finish()
        
    async def completed(self):
        self.done = True
        self.area.tasks.remove(self)
        self.coordination.tasks.remove(self)
        await self.clock.messages[0].delete()
        await self.clock.stop()
        await self.message.delete()

async def CoordinationRespond(messagearray, message):
    if messagearray[1].lower() == 'setup':
        try:
            areas = int(messagearray[2])
            participant = discord.utils.get(message.guild.roles, name=messagearray[3])
            specs = []
            for i in messagearray[4:len(messagearray)]:
               specs.append(discord.utils.get(message.guild.roles, name=i))
        except:
            await message.channel.send('An integer is needed for the first argument representing the number of areas.')
            return
        if participant == None:
            await message.channel.send('Could not find the participant role.')
            return
        if None in specs:
            await message.channel.send('One of the spectator role names was wrong.')
            return
        c = Coordination(message.guild, areas, participant, specs)
        CoordinationDictionary.update({message.guild:c})
        await c.channelSetup()
    else:
        try:
            c = CoordinationDictionary[message.guild]
        except:
            await message.channel.send('This must be set up first.')
        
    if messagearray[1].lower() == 'end':
        c.active = False
        await c.endtasks()
        CoordinationDictionary.pop(message.guild)
        for i in c.areas:
            await i.channel.delete()
        await c.announcementschannel.delete()
        await c.category.delete()
    
    if messagearray[1].lower() == 'start':
        await c.start()
        
    

async def onMessage(message):#triggered when anyone sends a message
    try:
        c = CoordinationDictionary[message.guild]
    except:
        return
    if c.participant in message.author.roles :
        for i in c.areas:
            if message.channel == i.channel:
                for j in i.tasks:
                    if message.content == j.letters:
                        await j.completed()
                        await message.channel.send('You completed a task.')
                        return
                await message.channel.send('You did not complete a task.')
                return
    