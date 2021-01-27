from Functions import botadmin
import random
bawplayers = []
async def RegisterBaWPlayer(user, message):
    player = BaWPlayer(user, channel = message.channel)
    bawplayers.append(player)
    
def UserRegisteredAsBaWPlayer(user):
    for player in bawplayers:
        if player.user == user:
            return player
    return False

class BaWPlayer:
    
    def __init__(self, player, opponent = None, channel = None):
        '''player must be a discord.user'''
        self.user = player
        self.opponent = opponent
        self.tiles = [0, 1, 2, 3, 4, 5, 6, 7, 8]
        self.wins = 0
        self.channel = channel #channel to respond in
        self.canPlay = False
        self.tileSubmitted = -1
        
    def setOpponent(self, opponent):
        '''
        opponent must be a BaWPlayer
        '''
        self.opponent = opponent
    
    def hasTile(self, i):
        return i in self.tiles
    
    def getTile(self, i):
        if i in self.tiles:
            self.tiles.remove(i)
            return True
        else:
            return False

async def BaWRespond(messagearray, message):
#black and white
#            if messagearray[1] == 'Register':
#                if len(message.mentions) == 0:
#                    if(UserRegisteredAsBaWPlayer(message.author) != False):
#                        await message.channel.send(message.author.display_name + ' is already registered.')
#                    else:
#                        await RegisterBaWPlayer(message.author, message)
#                else:
#                    for user in message.mentions:
#                        if(UserRegisteredAsBaWPlayer(user)):
#                            await message.channel.send(user.display_name + ' is already registered.')
#                            return
#                    for user in message.mentions:
#                        await RegisterBaWPlayer(user, message)
    if messagearray[1] == 'Match':
        #register
        if len(message.mentions) % 2 != 0:
            await message.channel.send('Tried to match opponents but there was an odd number of players.')
        else:
            for user in message.mentions:
                if(UserRegisteredAsBaWPlayer(user)):
                    await message.channel.send(user.display_name + ' is already in a match.')
                    return
            for user in message.mentions:
                await RegisterBaWPlayer(user, message)
            #match
            else:
                users = message.mentions
                for i in range(0, len(users), 2):
                    UserRegisteredAsBaWPlayer(users[i]).setOpponent(UserRegisteredAsBaWPlayer(users[i+1]))
                    UserRegisteredAsBaWPlayer(users[i+1]).setOpponent(UserRegisteredAsBaWPlayer(users[i]))
                    num = random.randrange(0, 2) + i
                    await message.channel.send('Matched ' + users[i].display_name + ' with ' + users[i+1].display_name + ". " + users[num].mention + " will play first.")
                    UserRegisteredAsBaWPlayer(users[num]).canPlay = True
    if messagearray[1] == 'Score':
        player = UserRegisteredAsBaWPlayer(message.author)
        if player != False:
            scoremessage = "The score in your game of Black and White against " + player.opponent.user.display_name + " is: " + player.user.display_name + " " + str(player.wins) + ", " + player.opponent.user.display_name + " " + str(player.opponent.wins) + "."
            await message.channel.send(scoremessage)
        else:
            await message.channel.send("You are not currently playing against anyone.")
    if messagearray[1] == 'Tiles':
        player = UserRegisteredAsBaWPlayer(message.author)
        if player != False:
            tilemessage = "Your remaining tiles in your game of Black and White against " + player.opponent.user.display_name + " are: "
            for tile in player.tiles:
                tilemessage += str(tile) + ", "
            tilemessage = tilemessage[:-2] + "."
            await message.channel.send(tilemessage)
        else:
            await message.channel.send("You are not currently playing against anyone.")
    if messagearray[1] == 'End':
        player = UserRegisteredAsBaWPlayer(message.author)
        if not player == False:
            scoremessage = "The game of Black and White against " + player.user.display_name +' and '+ player.opponent.user.display_name + " Has ended with a score of: " + player.user.display_name + " " + str(player.wins) + ", " + player.opponent.user.display_name + " " + str(player.opponent.wins) + "."
            await message.channel.send(scoremessage)
            bawplayers.remove(player.opponent)
            bawplayers.remove(player)
    if messagearray[1] == 'Play':
        if len(messagearray) > 2 and messagearray[2].isdigit():
            n = int(messagearray[2])
            player = UserRegisteredAsBaWPlayer(message.author)
            if player.canPlay:
                if n > -1 and n < 9 and player.getTile(n):
                    if(player.opponent.tileSubmitted == -1):
                        if n%2 == 0:
                            await player.channel.send(player.user.display_name + " has played a **black** tile. " + player.opponent.user.mention + ", it is your turn.")
                        else:
                            await player.channel.send(player.user.display_name + " has played a **white** tile. " + player.opponent.user.mention + ", it is your turn.")
                        player.tileSubmitted = n
                        player.canPlay = False
                        player.opponent.canPlay = True
                    else:
                        if n%2 == 0:
                            await player.channel.send(player.user.display_name + " has played a **black** tile.")
                        else:
                            await player.channel.send(player.user.display_name + " has played a **white** tile.")
                        if len(player.tiles) == 0:
                            if n > player.opponent.tileSubmitted:
                                await player.channel.send(player.user.display_name + " has won this round.")
                                player.wins += 1
                            elif n < player.opponent.tileSubmitted:
                                await player.channel.send(player.opponent.user.display_name + " has won this round.")
                                player.opponent.wins += 1
                            else:
                                await player.channel.send("This round was a draw.")
                            if player.wins > player.opponent.wins:
                                await player.channel.send(player.user.display_name + " has won their game of Black and White against " + player.opponent.user.display_name + ".")
                            elif player.wins < player.opponent.wins:
                                await player.channel.send(player.opponent.user.display_name + " has won their game of Black and White against " + player.user.display_name + ".")
                            else:
                                await player.channel.send("The game of Black and White between " + player.opponent.user.display_name + " and " + player.user.display_name + " was a draw.")
                            bawplayers.remove(player.opponent)
                            bawplayers.remove(player)
                        else:
                            if n > player.opponent.tileSubmitted:
                                await player.channel.send(player.user.display_name + " has won this round. " + player.user.mention + ", it is your turn.")
                                player.opponent.tileSubmitted = -1
                                player.wins += 1
                            elif n < player.opponent.tileSubmitted:
                                await player.channel.send(player.opponent.user.display_name + " has won this round. " + player.opponent.user.mention + ", it is your turn.")
                                player.opponent.tileSubmitted = -1
                                player.canPlay = False
                                player.opponent.canPlay = True
                                player.opponent.wins += 1
                            else:
                                await player.channel.send("This round was a draw. "+ player.user.mention + ", it is your turn.")
                                player.opponent.tileSubmitted = -1
                else:
                    await message.channel.send("You must enter a number that you have between 0 and 8")
            else:
                await message.channel.send("It is not your turn.")
        else:
            await message.channel.send("Use `H!BaW Play {number}` to play")