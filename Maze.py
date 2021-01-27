import discord
import random

MazeDictionary = {}

def product(l):
    result = 1
    for x in l: 
         result = result * x  
    return result  

class Maze:
    def __init__(self, guild, dimensions, wallchance):
        self.guild = guild
        self.dimensions = dimensions
        self.rooms = [] #organized into sub-dimensions (i.e.multi-dimensional)
        self.roomslist = [] #unorganized list (i.e. one-dimensional)
        self.wallchance = wallchance
        self.initRooms([self.rooms], [i for i in self.dimensions])
        self.players = []
        counter = 0
        self.addWalls()
        limit = int(1000000/product(self.dimensions))
        if product(self.dimensions) > 300:
            limit = 0
        while counter < limit and not self.checkWalls([[0 for i in range(len(self.dimensions))]], [], product(self.dimensions)):
            self.addWalls()
            counter += 1
        if counter >= limit:
            self.success = False
        else:
            self.success = True
        
    def initRooms(self, targets, dimensions):
        if len(dimensions) == 1:
            for i in targets:
                for j in range(dimensions[0]):
                    m = Room(self, self.guild)
                    i.append(m)
                    self.roomslist.append(m)
        else:
            newtargets = []
            for i in targets:
                for j in range(dimensions[0]):
                    m = []
                    i.append(m)
                    newtargets.append(m)
                    
            self.initRooms(newtargets, dimensions[1:])
    
    def getRoomFromCoords(self, coords):
        room = self.rooms
        for i in coords:
            room = room[i]
        return room
    
    def addWalls(self):
        for i in self.roomslist:
            i.walls = []
            for j in range(len(self.dimensions)):
                if random.random()*100 < self.wallchance:
                    i.walls.append(False)
                else:
                    i.walls.append(True)
                    
    def checkWalls(self, active, inactive, target):
        if len(active) + len(inactive) == target:
            return True
        elif len(active) == 0:
            return False
        else:
            newactive = []
            for i in active:
                inactive.append(i)
                for j in range(len(self.dimensions)):
                    if self.getRoomFromCoords(i).walls[j]:
                        coords = [k for k in i]
                        if self.dimensions[j] - 1 > coords[j]:
                            coords[j] += 1
                            if (not coords in active and not coords in inactive):
                                newactive.append(coords)
            return self.checkWalls(newactive, inactive, target)
    
    def getPlayerFromUser(self, user):
        for i in self.players:
            if i.user == user:
                return i
        return None
                    
class Room:
    def __init__(self, maze, guild):
        self.maze = maze
        self.guild = guild
        self.walls = []
            
class Player:
    def __init__(self, maze, user):
        self.maze = maze
        self.coordinates = [0 for i in range(len(self.maze.dimensions))]
        self.maze.players.append(self)
        self.user = user
        
    def checkWallsForMove(self, dimension, direction):
        if direction == 'i':
            if self.maze.dimensions[dimension] - 1 <= self.coordinates[dimension]:
                return None
            return self.maze.getRoomFromCoords(self.coordinates).walls[dimension]
        else:
            coords = [i for i in self.coordinates]
            coords[dimension] -= 1
            if coords[dimension] < 0:
                return None
            return self.maze.getRoomFromCoords(coords).walls[dimension]
            
    def roomString(self):
        s = ''
        for i in self.coordinates:
            s += str(i + 1) + '-'
        return s[:-1]
        
async def MazeRespond(messagearray, message):
    if messagearray[1].lower() == 'setup' and message.author.guild_permissions.administrator:
        m = Maze(message.guild, [int(i) for i in messagearray[3:]], int(messagearray[2]))
        if not m.success:
            await message.channel.send('Could not create the walls.')
            return
        MazeDictionary.update({message.guild: m})
        await message.channel.send('Setup Complete.')
        
    if messagearray[1].lower() == 'end' and message.author.guild_permissions.administrator:
        MazeDictionary.update({message.guild: None})
    
    if messagearray[1].lower() == 'move':
        try:
            player = MazeDictionary[message.guild].getPlayerFromUser(message.author)
            if player == None:
                await message.channel.send('You must be in a maze to use that.')
                return
        except:
            await message.channel.send('A maze needs to be set up first.')
            return
        if messagearray[2].lower() == 'inc' or messagearray[2].lower() == 'i' or messagearray[2].lower() == 'increase' or messagearray[2].lower() == 'up':
            direction = 'i'
        elif messagearray[2].lower() == 'dec' or messagearray[2].lower() == 'd' or messagearray[2].lower() == 'decrease' or messagearray[2].lower() == 'down':
            direction = 'd'
        else:
            await message.channel.send('The direction was invalid.')
            return
        n = int(messagearray[3]) - 1
        if n >= len(player.maze.dimensions) or n < 0:
            await message.channel.send('The dimension needs to be between 1 and ' + str(len(player.maze.dimensions)) + '.')
            return
        result = player.checkWallsForMove(n, direction)
        if result == True:
            if direction == 'i':
                player.coordinates[n] += 1
            else:
                player.coordinates[n] -= 1
            await message.channel.send('You successfuly moved to room ' + player.roomString() + '.')
        elif result == None:
            await message.channel.send('You can\'t move out-of-bounds.')
        else:
            await message.channel.send('You ran into a wall and couldn\'t move.')
            
    if messagearray[1].lower() == 'enter':
        try:
            maze = MazeDictionary[message.guild]
        except:
            await message.channel.send('A maze needs to be set up first.')
            return
        if maze == None:
            await message.channel.send('A maze needs to be set up first.')
            return
        if maze.getPlayerFromUser(message.author) == None:
            Player(maze, message.author)
            await message.channel.send('You entered the maze.')
        else:
            await message.channel.send('You are already in the maze.')
            
    if messagearray[1].lower() == 'leave':
        try:
            maze = MazeDictionary[message.guild]
        except:
            await message.channel.send('A maze needs to be set up first.')
            return
        if maze == None:
            await message.channel.send('A maze needs to be set up first.')
            return
        if maze.getPlayerFromUser(message.author) == None:
            await message.channel.send('You are not in the maze.')
        else:
            maze.players.remove(maze.getPlayerFromUser(message.author))
            await message.channel.send('You left the maze.')
            
                