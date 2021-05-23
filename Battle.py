#I've had the thought of allowing non-rectangle rooms in some ways but that would require overhauling a bunch of stuff throughout this entire module
#Basically, there are so many places where I assumed rectangular dungeons that changing it would require reviewing the entire code and rewriting a ton of it
#Considering the quality of this code, this isn't a terrible idea. But I also like having weekends during uni.

#there's a lot of complicated stuff going on in here, but creating new items is pretty simple at least. find the item class (and its children) to see examples

import discord
import random
from Functions import botadmin
import nest_asyncio as sy
#import csv
import Clock
from PIL import Image, ImageDraw, ImageFont, ImageColor
import os
import shutil
import cv2
import numpy as np
from os.path import isfile, join
import math

BattleDictionary = {}

def numberOfMatches():
    total = 0
    for i in BattleDictionary.values():
        if not i == None and i.active:
            total += 1
    return total

async def setup(guild):
    BattleDictionary.update({guild: None})
     
class Battle:
    def __init__(self, guild):
        self.Battlefield = [] #Battlefield[x][y] for individual room
        self.BattlePlayers = []
        self.BattleNPCs = []
        self.BattleCategory = []
        self.AnnouncementsChannel = None
        self.width = 0
        self.height = 0
        self.wallschance = []
        self.guild = guild
        self.spectatorrole = []
        self.active = True
        self.stagetimes = []
        self.poisonstage = 0
        self.poisondamage = None
        self.poisonstart = False
        self.poisonspeed = 7
        self.playerpositions = {}
        self.recordingtime = 0
        self.colors = list(ImageColor.colormap.keys())#grabs a list of colors from the imagecolor module
        self.recording = False
        self.bots = {}
        
    def reset(self):#yes, this really exists. I'm sorry.
        self.Battlefield = []
        self.BattlePlayers = []
        self.BattleCategory = []
        self.AnnouncementsChannel = None
        self.width = 0
        self.height = 0
        self.wallschance = []
        self.spectatorrole = []
        self.active = False
        self.stagetimes = []
        self.poisonstage = 0
        self.poisondamage = None
        self.poisonstart = False
        self.poisonspeed = 7
        self.playerpositions = {}
        self.recordingtime = 0
        self.colors = list(ImageColor.colormap.keys())
        self.recording = False
           
    async def StartRecording(self):
        dirname = str(self.guild.id)+'battleimages'
        os.mkdir(dirname)
        self.recording = True
        while self.recording:
            await sy.asyncio.sleep(1)
            self.recordingtime += 1
            drawMap(self.guild, True, dirname+'/image'+str(self.recordingtime)+'.png')
    
    async def poisonAdvance(self, time):
        done = await Clock.callAppClock(time, self.AnnouncementsChannel, 'Round ' + str(self.poisonstage + 1) + ' of poison spreading will occur in {time}.')
        if done:
            for i in range(self.height):
                if not self.Battlefield[self.poisonstage][i].poisoned:
                    await self.Battlefield[self.poisonstage][i].channel.send('This room is poisoned.')
                    self.Battlefield[self.poisonstage][i].poisoned = True
                if not self.Battlefield[self.width - self.poisonstage - 1][i].poisoned:
                    await self.Battlefield[self.width - self.poisonstage - 1][i].channel.send('This room is poisoned.')
                    self.Battlefield[self.width - self.poisonstage - 1][i].poisoned = True
            for i in range(self.width):
                if not self.Battlefield[i][self.poisonstage].poisoned:
                    await self.Battlefield[i][self.poisonstage].channel.send('This room is poisoned.')
                    self.Battlefield[i][self.poisonstage].poisoned = True
                if not self.Battlefield[i][self.height - self.poisonstage - 1].poisoned:
                    await self.Battlefield[i][self.height - self.poisonstage - 1].channel.send('This room is poisoned.')
                    self.Battlefield[i][self.height - self.poisonstage - 1].poisoned = True
        self.poisonstage += 1
        if self.poisonstage < len(self.stagetimes):
            await self.poisonAdvance(self.stagetimes[self.poisonstage])
        else:
            self.poisonstart = False
            
    async def PoisonCheck(self):
        while self.active:
            await sy.asyncio.sleep(1)
            for player in self.BattlePlayers:
                if player.room.poisoned:
                    player.poisonticks += 1
                    if player.poisonticks >= self.poisonspeed:
                        player.poisonticks = 0
                        if not self.poisondamage == None:
                            damage = self.poisondamage
                        else:
                            damage = self.poisonstage
                        player.maxhealth -= damage
                        player.health = min(player.health, player.maxhealth)
                        player.messages.append(await player.room.channel.send('You took ' + str(damage) + ' damage from poison.'))
                        if player.health <= 0:
                            await player.killed(None, None, None, None, 'They gasped their last breath as poisonous fog filled their lungs.')            
            
class Room:
    def __init__(self, Channel, X, Y, battle):
        self.battle = battle
        self.channel = Channel
        self.itemlist = []
        self.playerlist = []
        #I use 4 walls per room here which isn't ideal because it means each pair of rooms can have 2 walls between them and rooms can have walls facing the border of the dungeon
        self.northwall = random.choice(self.battle.wallschance)
        self.southwall = random.choice(self.battle.wallschance)
        self.eastwall = random.choice(self.battle.wallschance)
        self.westwall = random.choice(self.battle.wallschance)
        self.x = X
        self.y = Y
        self.poisoned = False
        self.customobject = None
        self.npclist = []
        
class Player:
    maxhealth = 20
    buffmax = 3
    def __init__(self, X, Y, User, BAttle):
        self.battle = BAttle
        self.map = False
        self.health = Player.maxhealth
        self.room = self.battle.Battlefield[X][Y]
        self.user = User
        self.x = X
        self.y = Y
        self.inventory = []
        self.messages = []
        self.alive = True
        self.meleeattack = 0
        self.meleedefense = 0
        self.rangedattack = 0
        self.rangeddefense = 0
        self.poisonticks = 0
        if len(self.battle.colors) > 0:
            self.colorstring = random.choice(self.battle.colors)
            self.battle.colors.remove(self.colorstring)
            self.color = ImageColor.getrgb(self.colorstring)
        else:
            self.colorstring = 'random'
            self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            
    async def enter(self, lastroom = None):
        Battlefield = self.battle.Battlefield
        self.room = Battlefield[self.x][self.y]
        if not lastroom == None:
            await lastroom.channel.set_permissions(self.user, read_messages=False, send_messages=False, read_message_history=False)
            lastroom.playerlist.remove(self)
        await self.room.channel.set_permissions(self.user, read_messages=True, send_messages=True, read_message_history=True)
        self.room.playerlist.append(self)
        for m in self.messages:
            await m.delete()
        self.messages = []
    
    async def killed(self, weapon, message, messagearray, attacker, source):
        self.alive = False
        self.battle.BattlePlayers.remove(self)
        self.room.playerlist.remove(self)
        AnnouncementsChannel = self.battle.AnnouncementsChannel
        for item in self.inventory:
            self.room.itemlist.append(item)
        await self.room.channel.send(self.user.mention + " has died. They dropped all the items in their inventory.")
        await AnnouncementsChannel.send(self.user.mention + " has died. " + source)
        await self.room.channel.set_permissions(self.user, read_messages=False, send_messages=False, read_message_history=False)
        for m in self.messages:
            await m.delete()
        
class NPC(Player):
    def __init__(self, X, Y, User, BAttle, health = 20):
        self.battle = BAttle
        self.map = False
        self.health = health
        self.room = self.battle.Battlefield[X][Y]
        self.user = User
        self.bot = BAttle.bots[User]
        self.x = X
        self.y = Y
        self.inventory = []
        self.messages = []
        self.alive = True
        self.poisonticks = 0
        if len(self.battle.colors) > 0:
            self.colorstring = random.choice(self.battle.colors)
            self.battle.colors.remove(self.colorstring)
            self.color = ImageColor.getrgb(self.colorstring)
        else:
            self.colorstring = 'random'
            self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    
    async def enter(self, lastroom = None):
        Battlefield = self.battle.Battlefield
        self.room = Battlefield[self.x][self.y]
        if not lastroom == None:
            remove = True
            lastroom.playerlist.remove(self)
            lastroom.npclist.remove(self)
            for i in lastroom.npclist:
                if i.user == self.user:
                    remove = False
            if remove:
                await lastroom.channel.set_permissions(self.user, read_messages=False, send_messages=False, read_message_history=False)
        await self.room.channel.set_permissions(self.user, read_messages=True, send_messages=True, read_message_history=True)
        self.room.playerlist.append(self)
        self.room.npclist.append(self)
        for m in self.messages:
            await m.delete()
        self.messages = []
        
    async def killed(self, weapon, message, messagearray, attacker, source):
        self.alive = False
        self.battle.BattlePlayers.remove(self)
        self.battle.BattleNPCs.remove(self)
        self.room.playerlist.remove(self)
        self.room.npclist.remove(self)
        AnnouncementsChannel = self.battle.AnnouncementsChannel
        for item in self.inventory:
            self.room.itemlist.append(item)
        await self.room.channel.send(self.user.mention + " has been slain.")
        await AnnouncementsChannel.send(self.user.mention + " has been slain.")
        remove = True
        for i in self.room:
            if i.user == self.user:
                remove = False
            if remove:
                await self.room.channel.set_permissions(self.user, read_messages=False, send_messages=False, read_message_history=False)
        for m in self.messages:
            await m.delete()
    
class Item:
    name = ""
    def __init__(self, BAttle):
        self.battle = BAttle
        self.uses = 1
        
    async def use(self, message, messagearray, user):
        pass

#non-weapon items should inherit the item class and use the use command
#melee weapons should inherit the weapon class and use the attack function
#ranged weapons should inherit the gun class and use the attack and fire function

class Map(Item):#good example of an item; just set use limits and code any effects into the use function
    name = "Map"
    def __init__(self, battle):
        self.battle = battle
        self.uses = 1
        
    async def use(self, message, messagearray, user):
        if not user.map:
            user.map = True
            user.messages.append(await message.channel.send('You can use maps now!'))
            user.inventory.remove(self)
        else:
            user.messages.append(await message.channel.send('You can already use maps.'))

class Compass(Item):
    name = "Compass"
    def __init__(self, battle):
        self.battle = battle
        self.uses = 4
        
    async def use(self, message, messagearray, user):
        battle = user.battle
        roomsize = math.hypot(battle.width, battle.height)
        s = ''
        for player in battle.BattlePlayers:
            if not player is user:
                dx = player.x - user.x
                dy = player.y - user.y
                d = math.hypot(dx, dy)
                frac = d/roomsize
                if frac == 0.0:
                    s += 'A player is in your room!\n'
                else:
                    if frac < .21:
                        distance = 'very close'
                    elif frac < .36:
                        distance = 'close' 
                    elif frac < .6:
                        distance = 'far' 
                    else:
                        distance = 'very far'
                    angle = math.degrees(math.atan2(dy, dx))
                    if angle < -157.5:
                        direction = 'west'
                    elif angle < -112.5:
                        direction = 'northwest'
                    elif angle < -67.5:
                        direction = 'north'
                    elif angle < -22.5:
                        direction = 'northeast'
                    elif angle < 22.5:
                        direction = 'east'
                    elif angle < 67.5:
                        direction = 'southeast'
                    elif angle < 112.5:
                        direction = 'south'
                    elif angle < 157.5:
                        direction = 'southwest'
                    else:
                        direction = 'west'
                    s += 'There is a player ' + distance + ' to the ' + direction + '.\n'
        user.messages.append(await message.channel.send(s))
        self.uses -= 1
        if self.uses == 0:
                user.messages.append(await message.channel.send('Your compass broke.'))
                user.inventory.remove(self)
        
class Potion(Item):
    name = "Potion"
    def __init__(self, battle):
        self.battle = battle
        self.uses = random.randrange(1, 4)
        
    async def use(self, message, messagearray, user):
        if user.health < Player.maxhealth:
            user.health = min(Player.maxhealth, user.health + 3)
            user.messages.append(await message.channel.send('You healed yourself to ' + str(user.health) + ' health.'))
            self.uses -= 1
            if self.uses == 0:
                user.messages.append(await message.channel.send('Your potion ran out.'))
                user.inventory.remove(self)
        else:
            user.messages.append(await message.channel.send('You are already at full health.'))
            
class Berries(Item):
    name = "Berries"
    def __init__(self, battle):
        self.battle = battle
        self.uses = 1
        self.regen = random.randrange(-6, 8) + random.randrange(-6, 8)
        
    async def use(self, message, messagearray, user):
        if user.health < Player.maxhealth:
            user.health = min(Player.maxhealth, user.health + self.regen)
            if self.regen == 0:
                user.messages.append(await message.channel.send('The berries had no effect.'))
            elif self.regen > 0:
                user.messages.append(await message.channel.send('The berries healed you to ' + str(user.health) + ' health.'))
            else:
                user.messages.append(await message.channel.send('The berries were poisonous. You took ' + str(-self.regen) + ' damage.'))
                if user.health <= 0:
                    await user.killed(None, None, None, None, 'Their berries betrayed them.')
            user.inventory.remove(self)
        else:
            user.messages.append(await message.channel.send('You are already at full health.'))

class Steroids(Item):
    name = "Steroids" 
    async def use(self, message, messagearray, user):
        if user.meleeattack < Player.buffmax:
            user.meleeattack += 1
            user.messages.append(await message.channel.send('Your melee attacks are now more powerful!'))
            user.inventory.remove(self)
        else:
            user.messages.append(await message.channel.send('You can\'t increase your melee attack more.'))
            
class Scope(Item):
    name = "Scope"  
    async def use(self, message, messagearray, user):
        if user.rangedattack < Player.buffmax:
            user.rangedattack += 1
            user.messages.append(await message.channel.send('Your ranged attacks are now more powerful!'))
            user.inventory.remove(self)
        else:
            user.messages.append(await message.channel.send('You can\'t increase your ranged attack more.'))
            
class Shield(Item):
    name = "Shield"
    async def use(self, message, messagearray, user):
        if user.meleedefense < Player.buffmax:
            user.meleedefense += 1
            user.messages.append(await message.channel.send('Your melee defense is now stronger!'))
            user.inventory.remove(self)
        else:
            user.messages.append(await message.channel.send('You can\'t increase your melee defense more.'))
            
class Vest(Item):
    name = "Vest"
    async def use(self, message, messagearray, user):
        if user.rangeddefense < Player.buffmax:
            user.rangeddefense += 1
            user.messages.append(await message.channel.send('Your ranged defense is now stronger!'))
            user.inventory.remove(self)
        else:
            user.messages.append(await message.channel.send('You can\'t increase your ranged defense more.'))
            
class Drill(Item):
    name = "Drill"
    async def use(self, message, messagearray, user):
        if not len(messagearray) == 4:
            return
        x = user.room.x-1
        y = user.room.y-1
        used = False
        try:
            if messagearray[3] == "North" or messagearray[3] == "north" or messagearray[3] == "N" or messagearray[3] == "n":
                if user.room.northwall or self.battle.Battlefield[x][y-1].southwall:
                    used = True
                    user.room.northwall = False
                    self.battle.Battlefield[x][y-1].southwall=False
            if messagearray[3] == "South" or messagearray[3] == "south" or messagearray[3] == "S" or messagearray[3] == "s":
                if user.room.southwall or self.battle.Battlefield[x][y+1].northwall:
                    used = True
                    user.room.southwall = False
                    self.battle.Battlefield[x][y+1].northwall=False
            if messagearray[3] == "West" or messagearray[3] == "west" or messagearray[3] == "W" or messagearray[3] == "w":
                if user.room.westwall or self.battle.Battlefield[x-1][y].eastwall:
                    used = True
                    user.room.westwall = False
                    self.battle.Battlefield[x-1][y].eastwall=False
            if messagearray[3] == "East" or messagearray[3] == "east" or messagearray[3] == "E" or messagearray[3] == "e":
                if user.room.eastwall or self.battle.Battlefield[x+1][y].westwall:
                    used = True
                    user.room.eastwall = False
                    self.battle.Battlefield[x+1][y].westwall=False
        except:
            user.messages.append(await user.room.channel.send('You can\'t drill out of bounds.'))
            return
        if used:
            user.messages.append(await user.room.channel.send('You drilled a hole in the wall.'))
            user.inventory.remove(self)
        else:
            user.messages.append(await user.room.channel.send('There was no wall blocking your path in the direction specified.'))
            
class Weapon(Item):
    name = ""
    def __init__(self, BAttle):
        self.battle = BAttle
        self.uses = 5
        self.damage = 2
        
    async def attack(self, message, messagearray, attacker):
        pass
    
class Melee(Weapon):
    name = "Fists"
    def __init__(self, BAttle):
        self.battle = BAttle
        self.uses = -1
        self.damage = 1
    
    async def attack(self, message, messagearray, attacker):
        if len(message.mentions) == 1:
            if getPlayerFromUser(message.mentions[0]) == None or not getPlayerFromUser(message.mentions[0]).room == attacker.room:
                attacker.messages.append(await message.channel.send("You must attack another player in your room."))
                return
            for player in attacker.room.playerlist:
                if player.user == message.mentions[0]:
                    dmg = max(self.damage + attacker.meleeattack - player.meleedefense, 1)
                    attacker.messages.append(await message.channel.send("You land a blow against " + player.user.name + "! They take " + str(dmg) + " damage."))
                    player.health -= dmg
                    if player.health < 1 and player.alive:
                        await player.killed(self, message, messagearray, attacker, attacker.user.name + ' stabbed them in the gut.')
                    self.uses -= 1
                    if self.uses == 0:
                        attacker.messages.append(await message.channel.send("Your " + self.name.lower() + " broke."))
                        attacker.inventory.remove(self)
        else:
           attacker.messages.append(await message.channel.send("You must mention a single player you are attacking."))

class Knife(Melee):
    name = "Knife"
    def __init__(self, BAttle):
        self.battle = BAttle
        self.uses = 6
        self.damage = 2
    
    async def attack(self, message, messagearray, attacker):
        await Melee.attack(self, message, messagearray, attacker)

class Machete(Melee):
    name = "Machete"
    def __init__(self, BAttle):
        self.battle = BAttle
        self.uses = 5
        self.damage = 3
    
    async def attack(self, message, messagearray, attacker):
        await Melee.attack(self, message, messagearray, attacker)
        
class Sword(Melee):
    name = "Sword"
    def __init__(self, BAttle):
        self.battle = BAttle
        self.uses = 4
        self.damage = 4
    
    async def attack(self, message, messagearray, attacker):
        await Melee.attack(self, message, messagearray, attacker)

class Lightsaber(Weapon):
    name = "Lightsaber"
    def __init__(self, BAttle):
        self.battle = BAttle
        self.uses = 3
        self.damage = 6
    
    async def attack(self, message, messagearray, attacker):
        await Melee.attack(self, message, messagearray, attacker)
        
class Gun(Weapon):
    name = "Pistol"
    def __init__(self, BAttle):
        self.battle = BAttle
        self.uses = 8
        self.damage = 1
        self.silent = False
    
    async def attack(self, message, messagearray, attacker):
        BattlePlayers = self.battle.BattlePlayers
        if not self.silent:
            for player in BattlePlayers:
                if player.alive and not (player == attacker or (player.x == attacker.x and player.y == attacker.y)):
                    player.messages.append(await player.room.channel.send("You hear a shot ring out from room " + str(attacker.x + 1) + "-" + str(attacker.y + 1)))
        fired = False
        if messagearray[3] == "North" or messagearray[3] == "north" or messagearray[3] == "N" or messagearray[3] == "n":
            await self.Fire(message, messagearray, attacker, 1)
            fired = True
        if messagearray[3] == "South" or messagearray[3] == "south" or messagearray[3] == "S" or messagearray[3] == "s":
            await self.Fire(message, messagearray, attacker, 2)
            fired = True
        if messagearray[3] == "West" or messagearray[3] == "west" or messagearray[3] == "W" or messagearray[3] == "w":
            await self.Fire(message, messagearray, attacker, 3)
            fired = True
        if messagearray[3] == "East" or messagearray[3] == "east" or messagearray[3] == "E" or messagearray[3] == "e":
            await self.Fire(message, messagearray, attacker, 4)
            fired = True
        if fired:
            self.uses -= 1
            if self.uses == 0:
                attacker.messages.append(await message.channel.send("Your " + self.name.lower() + " broke."))
                attacker.inventory.remove(self)
        
    async def Fire(self, message, messagearray, attacker, direction):
        Battlefield = self.battle.Battlefield
        BattlePlayers = self.battle.BattlePlayers
        width = self.battle.width
        height = self.battle.height
        Done = False
        CurrentRoom = attacker.room
        Cx = attacker.x
        Cy = attacker.y
        while not Done:
            if direction == 1:
                Cy -= 1
                if Cy < 0 or CurrentRoom.northwall or Battlefield[Cx][Cy].southwall:
                    attacker.messages.append(await message.channel.send("You hear your shot hit a wall in the distance."))
                    Done = True
            if direction == 2: 
                Cy += 1
                if Cy >= height or CurrentRoom.southwall or Battlefield[Cx][Cy].northwall:
                    attacker.messages.append(await message.channel.send("You hear your shot hit a wall in the distance."))
                    Done = True
            if direction == 3:
                Cx -= 1
                if Cx < 0 or CurrentRoom.westwall or Battlefield[Cx][Cy].eastwall:
                    attacker.messages.append(await message.channel.send("You hear your shot hit a wall in the distance."))
                    Done = True
            if direction == 4: 
                Cx += 1
                if Cx >= width or CurrentRoom.eastwall or Battlefield[Cx][Cy].westwall:
                    attacker.messages.append(await message.channel.send("You hear your shot hit a wall in the distance."))
                    Done = True
            if not Done:
                CurrentRoom = Battlefield[Cx][Cy]
                if(len(CurrentRoom.playerlist) > 0):
                    Done = True
                    victim = random.choice(CurrentRoom.playerlist)
                    dmg = max(self.damage + attacker.rangedattack - victim.rangeddefense, 1)
                    victim.health -= dmg
                    victim.messages.append(await victim.room.channel.send(victim.user.mention + ", You were shot and took " + str(dmg) + " damage."))
                    if victim.health < 1 and victim.alive:
                        await victim.killed(self, message, messagearray, attacker, attacker.user.name + ' shot them through the heart.')
                    for player in BattlePlayers:
                        if not player == victim:
                            player.messages.append(await player.room.channel.send("You hear a yelp of pain from room " + str(Cx + 1) + "-" + str(Cy + 1)))
                            
class Musket(Gun):
    name = "Musket"
    def __init__(self, battle):
        self.battle = battle
        self.uses = 6
        self.damage = 2
        self.silent = False
    
    async def attack(self, message, messagearray, attacker):
        await Gun.attack(self, message, messagearray, attacker)
        
    async def Fire(self, message, messagearray, attacker, direction):
        await Gun.Fire(self, message, messagearray, attacker, direction)
        
class Rifle(Gun):
    name = "Rifle"
    def __init__(self, battle):
        self.battle = battle
        self.uses = 5
        self.damage = 3
        self.silent = False
    
    async def attack(self, message, messagearray, attacker):
        await Gun.attack(self, message, messagearray, attacker)
        
    async def Fire(self, message, messagearray, attacker, direction):
        await Gun.Fire(self, message, messagearray, attacker, direction)

class Blaster(Gun):
    name = "Blaster"
    def __init__(self, battle):
        self.battle = battle
        self.uses = 4
        self.damage = 4
        self.silent = False
    
    async def attack(self, message, messagearray, attacker):
        await Gun.attack(self, message, messagearray, attacker)
        
    async def Fire(self, message, messagearray, attacker, direction):
        await Gun.Fire(self, message, messagearray, attacker, direction)
        
class Bow(Gun):
    name = "Bow"
    def __init__(self, battle):
        self.battle = battle
        self.uses = 6
        self.damage = 1
        self.silent = True
    
    async def attack(self, message, messagearray, attacker):
        await Gun.attack(self, message, messagearray, attacker)
        
    async def Fire(self, message, messagearray, attacker, direction):
        await Gun.Fire(self, message, messagearray, attacker, direction)
        
class Crossbow(Gun):
    name = "Crossbow"
    def __init__(self, battle):
        self.battle = battle
        self.uses = 4
        self.damage = 3
        self.silent = True
    
    async def attack(self, message, messagearray, attacker):
        await Gun.attack(self, message, messagearray, attacker)
        
    async def Fire(self, message, messagearray, attacker, direction):
        await Gun.Fire(self, message, messagearray, attacker, direction)
        
class Bomb(Weapon):
    name = "Bomb"
    def __init__(self, battle):
        self.battle = battle
        self.uses = 1
        self.room = None
        self.time = 5

    async def attack(self, message, messagearray, attacker):
        try:
            self.time = int(messagearray[3])
        except:
            pass
        attacker.inventory.remove(self)
        self.room = attacker.room
        done = await Clock.callAppClock(self.time, self.room.channel, 'A bomb will explode in {time}!')
        if done:
            await self.room.channel.send('A bomb exploded in this room.')
            await Bomb.explode(self)
        
    async def explode(self):
        self.room.northwall = True
        self.room.southwall = True
        self.room.eastwall = True
        self.room.westwall = True
        for player in self.room.playerlist:
            await player.killed(None, None, None, None, 'They got caught in a highly rapid exothermic reaction.')
        for player in self.battle.BattlePlayers:
            player.messages.append(await player.room.channel.send("You hear an explosion from room " + str(self.room.x + 1) + "-" + str(self.room.y + 1) + '!'))
        
class Rocket(Bomb):
    name = "Rocket"
    def __init__(self, battle):
        self.battle = battle
        self.uses = 1
        self.room = None

    async def attack(self, message, messagearray, attacker):
        if not len(messagearray) == 4:
            return
        if messagearray[3].capitalize() == "North" or messagearray[3].capitalize() == "N":
            await self.Fire(message, messagearray, attacker, 1)
        elif messagearray[3].capitalize() == "South" or messagearray[3].capitalize() == "S":
            await self.Fire(message, messagearray, attacker, 2)
        elif messagearray[3].capitalize() == "West" or messagearray[3].capitalize() == "W":
            await self.Fire(message, messagearray, attacker, 3)
        elif messagearray[3].capitalize() == "East" or messagearray[3].capitalize() == "E":
            await self.Fire(message, messagearray, attacker, 4)
        else:
            return
    
    async def Fire(self, message, messagearray, attacker, direction):
        self.room = attacker.room
        Battlefield = self.battle.Battlefield
        width = self.battle.width
        height = self.battle.height
        Done = False
        Cx = attacker.x
        Cy = attacker.y
        while not Done:
            if direction == 1:
                Cy -= 1
                if Cy < 0 or self.room.northwall or Battlefield[Cx][Cy].southwall:
                    Done = True
            if direction == 2: 
                Cy += 1
                if Cy >= height or self.room.southwall or Battlefield[Cx][Cy].northwall:
                    Done = True
            if direction == 3:
                Cx -= 1
                if Cx < 0 or self.room.westwall or Battlefield[Cx][Cy].eastwall:
                    Done = True
            if direction == 4: 
                Cx += 1
                if Cx >= width or self.room.eastwall or Battlefield[Cx][Cy].westwall:
                    Done = True
            if not Done:
                self.room = Battlefield[Cx][Cy]
                if(len(self.room.playerlist) > 0):
                    Done = True
        attacker.inventory.remove(self)      
        await self.room.channel.send('A rocket exploded in this room.')
        await self.explode()
        
    async def explode(self):
        self.room.northwall = True
        self.room.southwall = True
        self.room.eastwall = True
        self.room.westwall = True
        for player in self.room.playerlist:
            await player.killed(None, None, None, None, 'They just managed to dodge the rocket, before it exploded behind them anyways.')
        for player in self.battle.BattlePlayers:
            player.messages.append(await player.room.channel.send("You hear an explosion from room " + str(self.room.x) + "-" + str(self.room.y) + '!'))
        
async def move(message, ThisPlayer, newx, newy, direction):
    Battlefield = BattleDictionary[message.guild].Battlefield
    room = ThisPlayer.room
    try:
        if direction == 1 and (room.northwall or Battlefield[newx][newy].southwall):
            ThisPlayer.messages.append(await message.channel.send("You ran into a wall and could not move on."))
            return
        if direction == 2 and (room.southwall or Battlefield[newx][newy].northwall):
            ThisPlayer.messages.append(await message.channel.send("You ran into a wall and could not move on."))
            return
        if direction == 3 and (room.eastwall or Battlefield[newx][newy].westwall):
            ThisPlayer.messages.append(await message.channel.send("You ran into a wall and could not move on."))
            return
        if direction == 4 and (room.westwall or Battlefield[newx][newy].eastwall):
            ThisPlayer.messages.append(await message.channel.send("You ran into a wall and could not move on."))
            return
    except:
        ThisPlayer.messages.append(await message.channel.send("You can't move out of bounds."))
        return
    ThisPlayer.x = newx
    ThisPlayer.y = newy
    await ThisPlayer.enter(lastroom = room)

def getPlayer(message):
    for player in BattleDictionary[message.guild].BattlePlayers:
        if player.user == message.author:
            return player
    return None
     
def getPlayerFromUser(user):
    for player in BattleDictionary[user.guild].BattlePlayers:
        if player.user == user:
            return player
    return None
     
async def getRoom(message):
    Battlefield = BattleDictionary[message.guild].Battlefield
    ThisRoom = None
    for i in range(len(Battlefield)):
        for j in range(len(Battlefield[0])):
            if Battlefield[i][j].channel == message.channel:
                ThisRoom = Battlefield[i][j]
    if ThisRoom == None:
        await message.channel.send("Couldn't find the room.")
        return None
    else:
         return ThisRoom
     
def getItem(itemname):
    ThisItem = None
    for itemclass in all_subclasses(Item):
        if itemclass.name == itemname:
            ThisItem = itemclass
    return ThisItem

def drawMap(guild, drawplayers = False, fname = "map.png"):
    battle = BattleDictionary[guild]
    battlefield = battle.Battlefield
    if drawplayers:
        im = Image.new("RGB", (75*battle.width + 50, 75*battle.height + 150), (255, 255, 255))
    else:
        im = Image.new("RGB", (75*battle.width + 50, 75*battle.height + 50), (255, 255, 255))

    draw = ImageDraw.Draw(im)
    for i in range(battle.width):
        for j in range(battle.height):
            if battlefield[i][j].southwall or (j+1 < battle.height and battlefield[i][j+1].northwall):
                draw.line((i*75+25, (j+1)*75+25, (i+1)*75+25, (j+1)*75+25), fill=100)
            if battlefield[i][j].eastwall or (i+1 < battle.width and battlefield[i+1][j].westwall):
                draw.line(((i+1)*75+25, j*75+25, (i+1)*75+25, (j+1)*75+25), fill=100)
    wbegin = 25
    hbegin = 25
    hend = battle.height*75+25
    wend = battle.width*75+25
    draw.line((wbegin, hbegin, wbegin, hend), fill=200)
    draw.line((wbegin, hbegin, wend, hbegin), fill=200)
    draw.line((wbegin, hend, wend, hend), fill=200)
    draw.line((wend, hbegin, wend, hend), fill=200)
    alreadydrawn = {}
    for i in range(battle.width):
        for j in range(battle.height):
            alreadydrawn[(i, j)] = []
    if drawplayers:
        for player in battle.BattlePlayers:
            alreadydrawn[(player.x, player.y)].append(player)
        for key in alreadydrawn.keys():
            if len(alreadydrawn[key]) == 1:
                player = alreadydrawn[key][0]
                i = player.x*75+25+37
                j = player.y*75+25+37
                draw.rectangle((i - 5, j - 5, i + 6, j + 6), fill=player.color)
            elif len(alreadydrawn[key]) > 1:
                for k in range(len(alreadydrawn[key])):
                    player = alreadydrawn[key][k]
                    i = player.x*75+25+17 + (k % 3)*20
                    j = player.y*75+25+17 + int(k / 3)*20
                    draw.rectangle((i - 5, j - 5, i + 6, j + 6), fill=player.color)
        shift = 25
        yshift = hend + 15
        for player in battle.BattlePlayers:
            try:
                draw.text((shift, yshift), player.user.name[:12], fill=player.color)
                draw.text((shift, yshift + 15), 'Health: ' + str(player.health), fill=player.color)
            except:
                pass
            shift += 75
            if shift > battle.width * 75:
                shift = 25
                yshift += 35
    im.save(fname)
    return fname
def all_subclasses(cls):
    return set(cls.__subclasses__()).union([s for c in cls.__subclasses__() for s in all_subclasses(c)])#stolen from stackoverflow

def RoomsAvailable(guild, roomlist = None, roomstocheck = None, targetlength = None):#recursive function that checks how many rooms are connected to each other
    Battlefield = BattleDictionary[guild].Battlefield
    if roomlist == None and roomstocheck == None:
        roomlist = [Battlefield[0][0]]
        roomstocheck = [Battlefield[0][0]]
    if targetlength == None:
        targetlength = len(Battlefield) * len(Battlefield[0])
    if len(roomlist) >= targetlength:
        return True
    if len(roomstocheck) == 0:
        return False
    ThisRoom = roomstocheck[0]
    roomstocheck.remove(ThisRoom)
    x = ThisRoom.x - 1
    y = ThisRoom.y - 1
    if y > 0 and not (Battlefield[x][y-1] in roomlist or ThisRoom.northwall or Battlefield[x][y-1].southwall):
        roomstocheck.append(Battlefield[x][y-1])
        roomlist.append(Battlefield[x][y-1])
    if y < len(Battlefield[0])-1 and not (Battlefield[x][y+1] in roomlist or ThisRoom.southwall or Battlefield[x][y+1].northwall):
        roomstocheck.append(Battlefield[x][y+1])
        roomlist.append(Battlefield[x][y+1])
    if x > 0 and not (Battlefield[x-1][y] in roomlist or ThisRoom.westwall or Battlefield[x-1][y].eastwall):
        roomstocheck.append(Battlefield[x-1][y])
        roomlist.append(Battlefield[x-1][y])
    if x < len(Battlefield)-1 and not (Battlefield[x+1][y] in roomlist or ThisRoom.eastwall or Battlefield[x+1][y].westwall):
        roomstocheck.append(Battlefield[x+1][y])
        roomlist.append(Battlefield[x+1][y])
#    for i in roomlist:
#        print(str(i.x) + ", " + str(i.y))
    return RoomsAvailable(guild, roomlist, roomstocheck, targetlength)

def resetwalls(guild):
    Battlefield = BattleDictionary[guild].Battlefield
    wallschance = BattleDictionary[guild].wallschance
    for i in Battlefield:
        for room in i:
            room.northwall = random.choice(wallschance)
            room.southwall = random.choice(wallschance)
            room.eastwall = random.choice(wallschance)
            room.westwall = random.choice(wallschance)
    
def setWallsChance(n):
    wallschance = []
    for i in range(n):
        wallschance.append(False)
    wallschance.append(True)
    return wallschance

async def BattleRespond(messagearray, message):
    global BattleDictionary
    battle = BattleDictionary[message.guild]
    if (not battle == None) and (battle.active == True):
        Battlefield = battle.Battlefield 
        BattlePlayers= battle.BattlePlayers
        BattleCategory = battle.BattleCategory 
        AnnouncementsChannel = battle.AnnouncementsChannel 
        width = battle.width 
        height = battle.height 
        #wallschance = battle.wallschance
    else:
        if messagearray[1].capitalize() == 'Clear' and message.author.guild_permissions.administrator:
            for channel in message.guild.channels:
                if channel.name.startswith("room-"):
                    await channel.delete()
                
        if messagearray[1].capitalize() == 'Setup' and message.author.guild_permissions.administrator:
            b = Battle(message.guild)
            try:
                b.width = int(messagearray[2])
                b.height = int(messagearray[3])
                if b.width * b.height + len(message.guild.channels) + round((b.width * b.height + 1)/50) + 1 > 499:
                    await message.channel.send("Couldn't set up the battle because it would put the server over 500 channels")
                    b.reset()
                    return
            except:
                await message.channel.send("The width and height (third and fourth arguments) need to be numbers.")
                b.reset()
                return
            V = 0
            try:
                b.wallschance = setWallsChance(int(messagearray[4]))
                V = 1
            except:
                b.wallschance = setWallsChance(4)
            b.BattleCategory.append(await message.guild.create_category("Dungeon Section 1"))
            for i in messagearray[(4+V):]:
                b.spectatorrole.append(discord.utils.get(message.guild.roles, name=i))
            Perms = {message.guild.default_role: discord.PermissionOverwrite(read_messages=False)}
            for i in b.spectatorrole:
                Perms.update({i: discord.PermissionOverwrite(read_messages=True, send_messages=False, read_message_history=True)})
            b.AnnouncementsChannel = await message.guild.create_text_channel("Battle Announcements", category=b.BattleCategory[0], overwrites = Perms)
            for i in range(1, b.width+1):
                b.Battlefield.append([])
                for j in range(1, b.height+1):
                    if len(b.BattleCategory[-1].channels) < 50:
                        NewChannel = await message.guild.create_text_channel("Room " + str(i) + "-" + str(j), category=b.BattleCategory[-1], slowmode_delay = 2, overwrites = Perms)
                    else:
                        b.BattleCategory.append(await message.guild.create_category("Dungeon Section " + str(len(b.BattleCategory) + 1)))
                        NewChannel = await message.guild.create_text_channel("Room " + str(i) + "-" + str(j), category=b.BattleCategory[-1], slowmode_delay = 2, overwrites = Perms)
                    room = Room(NewChannel, i, j, b)
                    b.Battlefield[-1].append(room)
            BattleDictionary.update({message.guild: b})
            i = 0
            limit = 10000
            while not (RoomsAvailable(message.guild) or i > limit):
                i += 1
                resetwalls(message.guild)
            if i > limit:
                await message.channel.send("Could not create a wall setup with every room connected.")
                try:
                    for row in b.Battlefield:
                        for room in row:
                            await room.channel.delete()
                    await b.AnnouncementsChannel.delete()
                    for cat in b.BattleCategory:
                        await cat.delete()
                    b.reset()
                except:
                    b.reset()
                return
            await message.channel.send("Setup Complete.")
            await b.PoisonCheck()
        return
    
    if messagearray[1].lower() == 'spawn' and message.author.guild_permissions.administrator:
        #try:
            for i in range(2, len(messagearray), 2):
                try:
                    ThisItem = getItem(messagearray[i])
                    for j in range(int(messagearray[i+1])):
                        random.choice(random.choice(Battlefield)).itemlist.append(ThisItem(battle))
                except:
                    await message.channel.send('Could not spawn ' + messagearray[i] + ', proceeding to spawn other items.')
#        except:
#            print("blarglarg")
#            return
#    
    if messagearray[1].lower() == 'centeredspawn' and message.author.guild_permissions.administrator:
        #try:
            #print(Battlefield)
            l1 = len(Battlefield)+1
            l2 = len(Battlefield[0])+1
            l1distribution = [(l1/2-abs(l1/2-i))**2+1 for i in range(l1)][1:]
            l2distribution = [(l2/2-abs(l2/2-i))**2+1 for i in range(l2)][1:]
            l1distribution = [i/sum(l1distribution) for i in l1distribution]
            l2distribution = [i/sum(l2distribution) for i in l2distribution]
            for k in range(2, len(messagearray), 2):
                try:
                    #print(messagearray[k])
                    ThisItem = getItem(messagearray[k])
                    #print(ThisItem)
                    for j in range(int(messagearray[k+1])):
                        row = int(np.random.choice(range(l1-1), 1, p = l1distribution))
                        column = int(np.random.choice(range(l2-1), 1, p = l2distribution))
                        #print(Battlefield[row][column])
                        #print(Battlefield[row][column].itemlist)
                        Battlefield[row][column].itemlist.append(ThisItem(battle))  
                except:
                    await message.channel.send('Could not spawn ' + messagearray[i] + ', proceeding to spawn other items.')
    
    if messagearray[1].lower() == 'register' and message.author.guild_permissions.administrator:
        if len(message.mentions) > 0:
            for user in message.mentions:
                BattlePlayers.append(Player(random.randrange(0, width), random.randrange(0, height), user, battle))
                print(str(BattlePlayers[-1].x) + ", " + str(BattlePlayers[-1].y))
                await AnnouncementsChannel.set_permissions(user, read_messages=True, send_messages=False, read_message_history=True)
                await BattlePlayers[-1].enter()
        else:
            BattlePlayers.append(Player(random.randrange(0, width), random.randrange(0, height), message.author, battle))
            await BattlePlayers[-1].enter()
            
    if messagearray[1].lower() == 'registernpc' and message.author.guild_permissions.administrator:
        if len(message.mentions) > 0:
            for user in message.mentions:
                BattlePlayers.append(NPC(random.randrange(0, width), random.randrange(0, height), user, battle))
                BattlePlayers.append(BattlePlayers[-1])
                print(str(BattlePlayers[-1].x) + ", " + str(BattlePlayers[-1].y))
                #await AnnouncementsChannel.set_permissions(user, read_messages=True, send_messages=False, read_message_history=True)
                await BattlePlayers[-1].enter()
                
    if messagearray[1].lower() == 'activatebot' and message.author.guild_permissions.administrator:
        intents = discord.Intents(messages=True)
        for token in messagearray[2:]:
            pass
            
    if messagearray[1].lower() == 'registerat' and message.author.guild_permissions.administrator:
        loclist = []
        for i in messagearray:
            try:
                a = int(i)
                if a > 0:
                    if (len(loclist) % 2 == 0 and a <= width) or (len(loclist) % 2 == 1 and a <= height):
                        loclist.append(a)
            except:
                print(i)
        print(loclist)
        if len(message.mentions) > 0 and len(message.mentions) * 2 == len(loclist):
            for i in range(len(message.mentions)):
                user = message.mentions[i]
                BattlePlayers.append(Player(loclist[2*i] - 1, loclist[2*i + 1] - 1, user, battle))
                print(str(BattlePlayers[-1].x) + ", " + str(BattlePlayers[-1].y))
                await AnnouncementsChannel.set_permissions(user, read_messages=True, send_messages=False, read_message_history=True)
                await BattlePlayers[-1].enter()

    if messagearray[1].lower() == 'recording' and message.author.guild_permissions.administrator:
        await battle.StartRecording()
        
    if messagearray[1].lower() == 'stoprecording' and message.author.guild_permissions.administrator:
        battle.recording = False
        pathIn= str(message.guild.id)+'battleimages/'
        pathOut = 'battlevid.avi'
        try:
            fps = int(messagearray[2])
        except:
            fps = 4
        frame_array = []
        files = [f for f in os.listdir(pathIn) if isfile(join(pathIn, f))]
        #for sorting the file names properly
        dirsize = getFolderSize(pathIn)
        
        if dirsize > 500000:#if this is to large the bot might crash
            shutil.make_archive('battleimages', 'zip', pathIn)
            try:
                await message.channel.send(file = discord.File('battleimages.zip'))
                os.remove('battleimages.zip')
                await message.channel.send("The file was to large to be processed with the bot. You can turn the pictures into a video yourself, or contact Quinn so he can do it.")
            except:
                await message.channel.send("There was a problem sending the video, most likely the size was over the file limit. Contact Quinn for assistance.")
            shutil.rmtree(pathIn)
        for i in range(len(files)):
            filename=pathIn + files[i]
            #reading each files
            img = cv2.imread(filename)
            height, width, layers = img.shape
            size = (width,height)
            
            #inserting the frames into an image array
            frame_array.append(img)
        out = cv2.VideoWriter(pathOut,cv2.VideoWriter_fourcc(*'DIVX'), fps, size)
        for i in range(len(frame_array)):
            # writing to a image array
            out.write(frame_array[i])
        out.release()
        await message.channel.send(file = discord.File(pathOut))
        os.remove(pathOut)
        shutil.rmtree(pathIn)   
    
    if messagearray[1].lower() == 'poison' and message.author.guild_permissions.administrator:
        for i in messagearray[2:]:
            battle.stagetimes.append(int(i))
        if not battle.poisonstart:
            battle.poisonstart = True
            await battle.poisonAdvance(battle.stagetimes[0])
            
    if messagearray[1].lower() == 'poisondamage' and message.author.guild_permissions.administrator:
        battle.poisondamage = int(messagearray[2])
        
    if messagearray[1].lower() == 'poisonspeed' and message.author.guild_permissions.administrator:
        battle.poisonspeed = int(messagearray[2])
        
    if messagearray[1].capitalize() == 'End' and message.author.guild_permissions.administrator:
        print(battle.playerpositions)
        try:
            for row in Battlefield:
                for room in row:
                    await room.channel.delete()
            await AnnouncementsChannel.delete()
            for cat in BattleCategory:
                await cat.delete()
            battle.reset()
        except:
            battle.reset()
            
    if messagearray[1].lower() == 'clear' and message.author.guild_permissions.administrator:#if the bot gets shut down or whatever, end won't remove the battle channels.
        #In that case clear can delete the channels by looking for channels that look like battle channels
        for channel in message.guild.channels:
            if channel.name.startswith("room-"):
                await channel.delete()
        if not battle == None:
            battle.active = False
                
    if messagearray[1].capitalize() == 'Move':
        if not message.channel.category in BattleCategory:
            await message.channel.send("You must enter that in your dungeon room.")
            return
        ThisPlayer = getPlayer(message)
        if ThisPlayer == None:
            await message.channel.send("You must be playing in a battle to use that.")
            return
        if messagearray[2] == "North" or messagearray[2] == "north" or messagearray[2] == "N" or messagearray[2] == "n":
            if ThisPlayer.y == 0:
                ThisPlayer.messages.append(await message.channel.send("You can't move out of bounds."))
                return
            await move(message, ThisPlayer, ThisPlayer.x, ThisPlayer.y-1, 1)
        if messagearray[2] == "South" or messagearray[2] == "south" or messagearray[2] == "S" or messagearray[2] == "s":
            if ThisPlayer.y == height - 1:
                ThisPlayer.messages.append(await message.channel.send("You can't move out of bounds."))
                return
            await move(message, ThisPlayer, ThisPlayer.x, ThisPlayer.y+1, 2)
        if messagearray[2] == "West" or messagearray[2] == "west" or messagearray[2] == "W" or messagearray[2] == "w":
            if ThisPlayer.x == 0:
                ThisPlayer.messages.append(await message.channel.send("You can't move out of bounds."))
                return
            await move(message, ThisPlayer, ThisPlayer.x-1, ThisPlayer.y, 4)
        if messagearray[2] == "East" or messagearray[2] == "east" or messagearray[2] == "E" or messagearray[2] == "e":
            if ThisPlayer.x == width - 1:
                ThisPlayer.messages.append(await message.channel.send("You can't move out of bounds."))
                return
            await move(message, ThisPlayer, ThisPlayer.x+1, ThisPlayer.y , 3)
            
    if messagearray[1].capitalize() == 'Wall' and message.author.guild_permissions.administrator:
        ThisRoom = await getRoom(message)
        if ThisRoom == None:
            return
        if messagearray[2] == "North" or messagearray[2] == "north" or messagearray[2] == "N" or messagearray[2] == "n":
            ThisRoom.northwall = not ThisRoom.northwall
        if messagearray[2] == "South" or messagearray[2] == "south" or messagearray[2] == "S" or messagearray[2] == "s":
            ThisRoom.southwall = not ThisRoom.southwall
        if messagearray[2] == "West" or messagearray[2] == "west" or messagearray[2] == "W" or messagearray[2] == "w":
            ThisRoom.westwall = not ThisRoom.westwall
        if messagearray[2] == "East" or messagearray[2] == "east" or messagearray[2] == "E" or messagearray[2] == "e":
            ThisRoom.eastwall = not ThisRoom.eastwall
    
    if messagearray[1].capitalize() == 'Custommessage' and message.author.guild_permissions.administrator:
        ThisRoom = await getRoom(message)
        if ThisRoom == None:
            return
        m = ''
        for i in messagearray[2:]:
            m += i + ' '
        m = m[:-1]
        ThisRoom.customobject = m
        m = await message.channel.send('The custom message was set.')
        await message.delete()
        await sy.asyncio.sleep(1)
        await m.delete()
    if messagearray[1].capitalize() == 'Give' and message.author.guild_permissions.administrator:
        players = []
        for ment in message.mentions:
            for player in battle.BattlePlayers:
                if player.user == ment:
                    players.append(player)
        for i in range(2 + len(message.mentions), len(messagearray), 2):
                try:
                    ThisItem = getItem(messagearray[i])
                    for j in range(int(messagearray[i+1])):
                        for k in players:
                            k.inventory.append(ThisItem(battle))
                except:
                    await message.channel.send('Could not give ' + messagearray[i] + ', proceeding to give other items.')
                        
    if messagearray[1].capitalize() == 'Attack':
        if not message.channel.category in BattleCategory:
            await message.channel.send("You must enter that in your dungeon room.")
            return
        ThisPlayer = getPlayer(message)
        if ThisPlayer == None:
            await message.channel.send("You must be playing in a battle to use that.")
            return
        if messagearray[2].capitalize() == 'Fists':
            m = Melee(battle)
            await m.attack(message, messagearray, ThisPlayer)
            return
        else:
            for item in ThisPlayer.inventory:
                if item.name == messagearray[2].capitalize() and issubclass(item.__class__, Weapon):
                    try:
                        await item.attack(message, messagearray, ThisPlayer)
                        return
                    except:
                        pass
                
    if messagearray[1].capitalize() == 'Use':
        if not message.channel.category in BattleCategory:
            await message.channel.send("You must enter that in your dungeon room.")
            return
        ThisPlayer = getPlayer(message)
        if ThisPlayer == None:
            await message.channel.send("You must be playing in a battle to use that.")
            return
        for item in ThisPlayer.inventory:
            if item.name == messagearray[2].capitalize():
                await item.use(message, messagearray, ThisPlayer)
                return
                
    if messagearray[1].capitalize() == 'Drop':
        num = 0
        if len(messagearray) > 3:
            try:
                num = int(messagearray[3]) - 1
            except:
                return
        if not message.channel.category in BattleCategory:
            await message.channel.send("You must enter that in your dungeon room.")
            return
        ThisPlayer = getPlayer(message)
        if ThisPlayer == None:
            await message.channel.send("You must be playing in a battle to use that.")
            return
        for item in ThisPlayer.inventory:
            if item.name == messagearray[2].capitalize():
                if num == 0:
                    ThisPlayer.inventory.remove(item)
                    ThisPlayer.room.itemlist.append(item)
                    ThisPlayer.messages.append(await message.channel.send("You dropped the " + item.name.lower() + "."))
                    return
                else:
                    num -= 1

    if messagearray[1].capitalize() == 'Inventory':
        ThisPlayer = getPlayer(message)
        if ThisPlayer == None:
            await message.channel.send("You must be playing in a battle to use that.")
            return
        if not message.channel.category in BattleCategory:
            await message.channel.send("You must enter that in your dungeon room.")
            return
        m = "These are the items you currently have:\n"
        for item in ThisPlayer.inventory:
            m += item.name +  " with " + str(item.uses) + " use(s) left.\n"
        ThisPlayer.messages.append(await message.channel.send(m))
    
    if messagearray[1].capitalize() == 'Status':
        ThisPlayer = getPlayer(message)
        if ThisPlayer == None:
            await message.channel.send("You must be playing in a battle to use that.")
            return
        if not message.channel.category in BattleCategory:
            await message.channel.send("You must enter that in your dungeon room.")
            return
        m = ""
        m += str(ThisPlayer.health) + " health left.\n"
        print(str(ThisPlayer.maxhealth))
        m += "Melee damage boost: " + str(ThisPlayer.meleeattack) + "\n"
        m += "Ranged damage boost: " + str(ThisPlayer.rangedattack) + "\n"
        m += "Melee defense boost: " + str(ThisPlayer.meleedefense) + "\n"
        m += "Ranged defense boost: " + str(ThisPlayer.rangeddefense) + "\n"
        ThisPlayer.messages.append(await message.channel.send(m))
        
    if messagearray[1].capitalize() == 'Map':
        if message.author.guild_permissions.administrator:
            await message.channel.send(file = discord.File(fp = drawMap(message.guild, True)))
            return
        ThisPlayer = getPlayer(message)
        if ThisPlayer == None:
            return
        if not ThisPlayer.map:
            ThisPlayer.messages.append(await message.channel.send("You don't have a map."))
            return
        ThisPlayer.messages.append(await message.channel.send(file = discord.File(fp = drawMap(message.guild))))
        
    if messagearray[1].capitalize() == 'Search':
        ThisPlayer = getPlayer(message)
        if ThisPlayer == None:
            await message.channel.send("You must be playing in a battle to use that.")
            return
        if not message.channel.category in BattleCategory:
            await message.channel.send("You must enter that in your dungeon room.")
            return
        m = ''
        if not ThisPlayer.room.customobject == None:
            m += ThisPlayer.room.customobject + '\n'
        m += "These are the items currently in this room:\n"
        for item in ThisPlayer.room.itemlist:
            m += item.name + " with " + str(item.uses) + " use(s) left.\n"
        ThisPlayer.messages.append(await message.channel.send(m))
        
    if messagearray[1].capitalize() == 'Scout':
        ThisPlayer = getPlayer(message)
        if ThisPlayer == None:
            await message.channel.send("You must be playing in a battle to use that.")
            return
        if not message.channel.category in BattleCategory:
            await message.channel.send("You must enter that in your dungeon room.")
            return
        m = ""
        x = ThisPlayer.room.x-1
        y = ThisPlayer.room.y-1
        if y > 0:
            if ThisPlayer.room.northwall or battle.Battlefield[x][y-1].southwall:
                m += 'There is a wall to the north.\n'
        if y < battle.height - 1:
            if ThisPlayer.room.southwall or battle.Battlefield[x][y+1].northwall:
                m += 'There is a wall to the south.\n'
        if x > 0:
            if ThisPlayer.room.westwall or battle.Battlefield[x-1][y].eastwall:
                m += 'There is a wall to the west.\n'
        if x < battle.width - 1:
            if ThisPlayer.room.eastwall or battle.Battlefield[x+1][y].westwall:
                m += 'There is a wall to the east.\n'
        if m == "":
            m = 'There are no walls bordering this room.'
        ThisPlayer.messages.append(await message.channel.send(m))
        
    if messagearray[1].capitalize() == 'Get':
        num = 0
        if len(messagearray) > 3:
            try:
                num = int(messagearray[3]) - 1
            except:
                return
        ThisPlayer = getPlayer(message)
        if ThisPlayer == None:
            await message.channel.send("You must be playing in a battle to use that.")
            return
        if not message.channel.category in BattleCategory:
            await message.channel.send("You must enter that in your dungeon room.")
            return
        for item in ThisPlayer.room.itemlist:
            if item.name == messagearray[2]:
                if num == 0:
                    ThisPlayer.inventory.append(item)
                    ThisPlayer.room.itemlist.remove(item)
                    ThisPlayer.messages.append(await message.channel.send("You picked up the " + item.name.lower() + "."))
                    return
                else:
                    num -= 1
                    
    if messagearray[1].capitalize() == 'Remove' and message.author.guild_permissions.administrator:
        for user in message.mentions:
            ThisPlayer = getPlayerFromUser(user)
            ThisPlayer.room.playerlist.remove(Player)
            BattlePlayers.remove(ThisPlayer)

async def onMessage(message):#triggered when anyone sends a message
    battleroom = False
    if not (BattleDictionary[message.guild] == None or BattleDictionary[message.guild].active == False):
        for i in BattleDictionary[message.guild].Battlefield:
            for j in i:
                if j.channel == message.channel:
                    battleroom = j
        if not battleroom == False:
            ThisPlayer = getPlayer(message)
            if not ThisPlayer == None:
                ThisPlayer.messages.append(message)
                
def getFolderSize(folder):
    total_size = os.path.getsize(folder)
    for item in os.listdir(folder):
        itempath = os.path.join(folder, item)
        if os.path.isfile(itempath):
            total_size += os.path.getsize(itempath)
        elif os.path.isdir(itempath):
            total_size += getFolderSize(itempath)
    return total_size