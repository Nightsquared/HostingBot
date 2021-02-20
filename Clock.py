import nest_asyncio as sy
import discord
import time as t
clocks = []

class Clock():
    def __init__(self, startingtime, teams, channel):
        self.teams = teams
        self.startingtime = startingtime
        self.times = [startingtime for i in teams]
        self.abstimes = [startingtime for i in teams]
        self.absstartingtime = t.time()
        self.currentabsturntime = self.absstartingtime
        self.currentteam = teams[0]
        self.currentteamindex = 0
        self.channel = channel
        self.messages = []
        self.ticktime = .4
        self.paused = False
        self.pausemessages = []
        
    async def start(self):
        for i in self.teams:
            self.messages.append(await self.channel.send(i.name + " time: " + time(self.startingtime)))
        await self.channel.send(self.teams[0].name + " starts.")
        for i in self.messages:
            await i.pin()
        await sy.asyncio.sleep(self.ticktime)
        
        while self in clocks:
            await sy.asyncio.sleep(self.ticktime)
            await self.tick()
        
    async def tick(self):
        #print(self.times)
        #print(self.abstimes)
        #print(self.currentabsturntime)
        #self.times[self.currentteamindex] -= 1
        if not self.paused and self.update():
            await self.messages[self.currentteamindex].edit(content = (self.currentteam.name + " time: " + time(self.times[self.currentteamindex])))
            if self.times[self.currentteamindex] < 1:
                await self.channel.send(self.currentteam.name + " ran out of time.")
                global clocks
                clocks.remove(self)
                for i in self.messages:
                    await i.unpin()
                for i in self.pausemessages:
                    await i.delete()
                return
        
    async def turn(self, message, stop = False):
        self.update()
        if(len(self.teams) == 1) or stop:
            await self.channel.send("Timer stopped.")
            global clocks
            clocks.remove(self)
            for i in self.messages:
                await i.unpin() 
            for i in self.pausemessages:
                    await i.delete()
            return
        #self.interrupt += 1
        self.currentteamindex += 1
        if self.currentteamindex >= len(self.teams):
            self.currentteamindex = 0
        self.currentteam = self.teams[self.currentteamindex]
        await self.channel.send(self.currentteam.name + ", it is your turn")
#        await sy.asyncio.sleep(self.ticktime)
#        await self.tick()

    async def pause(self, message):
        self.paused = True
        self.update()
        await self.messages[self.currentteamindex].edit(content = (self.currentteam.name + " time: " + time(self.times[self.currentteamindex])))
        self.pausemessages.append(await self.channel.send("Timer paused by " + str(message.author.name) + '.'))
        if self.times[self.currentteamindex] < 1:
            await self.channel.send(self.currentteam.name + " ran out of time.")
            global clocks
            clocks.remove(self)
            for i in self.messages:
                await i.unpin()
            for i in self.pausemessages:
                await i.delete()
            return
        
    async def unpause(self, message):
        thistime = t.time()
        self.abstimes[self.currentteamindex] += thistime - self.currentabsturntime
        self.paused = False
        self.pausemessages.append(await self.channel.send("Timer unpaused by " + str(message.author.name) + '.'))
        
    def update(self):
        r = False
        thistime = t.time()
        if not int(self.abstimes[self.currentteamindex]) == int(self.abstimes[self.currentteamindex] + self.currentabsturntime - thistime):
            r = True
        self.abstimes[self.currentteamindex] -= thistime - self.currentabsturntime
        self.currentabsturntime = thistime
        for i in range(len(self.abstimes)):
            #print(str(self.abstimes[i]))
            self.times[i] = int(self.abstimes[i])
        return r
        
def time(n):
    s = ""
    if n > 3600:
        s += str(int(n/3600)) + ':'
        n %= 3600
    if n > 60 or len(s) > 0:
        s1 = str(int(n/60))
        while len(s1) < 2:
            s1 = '0' + s1
        s += s1 + ':'
        n %= 60
    s1 = str(n)
    if len(s) > 0:
        while len(s1) < 2:
            s1 = '0' + s1
        return s + s1
    else:
        return s1
        
async def ClockRespond(messagearray, message):
    if messagearray[1].lower() == "turn":
        for i in clocks:
            if i.channel == message.channel and (i.currentteam == message.author or i.currentteam in message.author.roles or message.author.guild_permissions.administrator):
                await i.turn(message)
        return
    if messagearray[1].lower() == "stop":
        for i in clocks:
            if i.channel == message.channel and (i.currentteam == message.author or i.currentteam in message.author.roles or message.author.guild_permissions.administrator):
                await i.turn(message, stop = True)
        return
    if messagearray[1].lower() == "pause":
        for i in clocks:
            if i.channel == message.channel and (i.currentteam == message.author or i.currentteam in message.author.roles or message.author.guild_permissions.administrator):
                await i.pause(message)
        return
    if messagearray[1].lower() == "unpause":
        for i in clocks:
            if i.channel == message.channel and (i.currentteam == message.author or i.currentteam in message.author.roles or message.author.guild_permissions.administrator):
                await i.unpause(message)
#    if messagearray[1] == "AppClockTest":
#        clocks.append(AppClock(30, message.channel, 'the time left is {time}'))
#        done = await clocks[-1].start()
#        if done:
#            await message.channel.send ('Done.')
    teams = []
    for i in messagearray[2:]:
        teams.append(discord.utils.get(message.guild.roles, name=i))
        if teams[-1] == None:
            return
    if len(teams) > 0:
        clocks.append(Clock(int(messagearray[1]), teams, message.channel))
        await clocks[-1].start()
    else:       
        try:            
            clocks.append(Clock(int(messagearray[1]), [message.author], message.channel))
            await clocks[-1].start()
        except:
            pass

class AppClock():
    def __init__(self, startingtime, channel, message, donemessage = "Time's up!", pin = True):
        self.startingtime = startingtime
        self.absstartingtime = t.time()
        self.time = self.startingtime
        self.lastupdatetime = self.absstartingtime
        self.channel = channel
        self.messages = []
        self.ticktime = .4
        self.message = message
        self.finished = True
        self.donemessage = donemessage
        self.pin = pin
        
    async def start(self):
        self.messages.append(await self.channel.send(self.message.replace('{time}', time(self.startingtime))))
        if self.pin:
            for i in self.messages:
                await i.pin()
        await sy.asyncio.sleep(self.ticktime)
        
        while self in clocks:
            await sy.asyncio.sleep(self.ticktime)
            await self.tick()
        return self.finished
    
    async def tick(self):
        global clocks
        #self.times[self.currentteamindex] -= 1
        if self.update():
            #print(self.currentabsturntime)
            try:
                await self.messages[0].edit(content = (self.message.replace('{time}', time(self.time))))
                if self.time < 1:
                    if not self.donemessage == False:
                        await self.channel.send(self.donemessage)
                    clocks.remove(self)
                    if self.pin:
                        for i in self.messages:
                            await i.unpin()
                    return
            except:
                clocks.remove(self)
    
    async def stop(self):
        self.finished = False
        clocks.remove(self)
        if self.pin:
            for i in self.messages:
                await i.unpin()
        return self.messages
                
    def update(self):
        r = False
        thistime = t.time()
        if not int(self.lastupdatetime) == int(thistime):
            r = True
            self.lastupdatetime = thistime
        self.time = int(self.absstartingtime - thistime + self.startingtime)
        return r

async def callAppClock(time, channel, timemessage, donemessage = "Time's up!", pin = True):
    clocks.append(AppClock(time, channel, timemessage, donemessage, pin))
    done = await clocks[-1].start()
    return done
    