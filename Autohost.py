import Clock
import nest_asyncio as sy
import discord
import random as r

game = None

class Game:
    tribeweights = {
        2:45,
        3:35,
        4:15,
        5:5
        }
    
    finalistweights = {
        2:40,
        3:60,
        }
    
    swaptimeweights = {
        1:7,
        2:20,
        3:30,
        4:28,
        5:10,
        6:4,
        7:1
        }
    
    mergeweights = {
        -2:3,
        -1:15,
        0:40,
        1:35,
        2:7
        }
    
    swaptimeweights = {
        1:7,
        2:20,
        3:30,
        4:28,
        5:10,
        6:4,
        7:1
        }
    
    def __init__(self, guild, roundtime = 300, registertime = 1800, players = -1):
        self.roundtime = roundtime
        self.registertime = registertime
        self.targetplayercount = players
        self.guild = guild
        
    async def registerphase(self):
        self.official = await self.guild.create_category('Official')
        self.instructions = await self.official.create_text_channel('Instructions')
        self.instructionsmessage = await self.instructions.send('Instructions here.')
        self.treemail = await self.official.create_text_channel('Treemail')
        self.registermessage = await self.treemail.send('React to this message to play!')
        done = await Clock.callAppClock(self.registertime, self.treemail, 'The game will start in {time}.')
        if done:
            await self.start()
                
    async def start(self):
        await sy.asyncio.sleep(2)
        self.registermessage = await self.treemail.fetch_message(self.registermessage.id)
        self.registrants = []
        for reaction in self.registermessage.reactions:
            users = await reaction.users().flatten()
            for user in users:
                if not user in self.registrants and user in self.guild.members:
                    self.registrants.append(user)
        r.shuffle(self.registrants)
        if self.targetplayercount > -1:
            self.registrants = self.registrants[self.targetplayercount:]
        self.players = [Player(user) for user in self.registrants]
        print(self.players)
        self.playercount = 16#len(self.players)
        #generate game events
        self.targetfinalists = r.choices([i for i in Game.finalistweights.keys()], [i for i in Game.finalistweights.values()])
        options = []
        for i in range(self.playercount):
            if self.playercount*.45 <= i and self.playercount*.70 >= i and not i%self.targetfinalists==0:
                options.append(i)
        self.targetjury = r.choice(options)#maybe weight towards middle
        self.targetmerge = self.targetjury + r.choices([i for i in Game.mergeweights.keys()], [i for i in Game.mergeistweights.values()])

class Player:
    def __init__(self, user):
        self.user = user
        self.tribe = None
        self.vote = None
        
async def AutohostRespond(messagearray, message):
    global game
    if messagearray[1].lower() == 'setup':
        if not game == None:
            await message.channel.send('There is a game in progress.')
            return
        try:
            roundtime = int(messagearray[2])
        except:
            roundtime = 300
        try:
            registertime = int(messagearray[3])
        except:
            registertime = 1800
        try:
            players = int(messagearray[4])
        except:
            players = -1
        game = Game(message.guild, roundtime, registertime, players)
        await game.registerphase()