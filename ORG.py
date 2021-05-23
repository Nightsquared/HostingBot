import discord
import json
from Functions import botadmin
import datetime
import random as r
import Comms
orgs = {}

wordfile = open('wordlist.txt', 'r')
wordlist = []
for i in wordfile:
    wordlist.append(i[:-1])
wordfile.close()

class org:
    def __init__(self, guild, Episode = '1', SpectatorRoleNames = [], TribeRoleNames = [], AllianceCategoryName = None, Description = None, RequestableRoleNames = [], Announcement = '{tribeping} requested by {requester}'):
        self.RequestRoleMode = True
        self.guild = guild
        self.guildID = guild.id
        self.Episode = Episode
        self.SpectatorRoleNames = SpectatorRoleNames
        self.TribeRoleNames = TribeRoleNames
        self.AllianceCategoryName = AllianceCategoryName
        self.AllianceCategory = discord.utils.get(guild.categories, name=AllianceCategoryName)
        self.SpectatorRoles = []
        self.TribeRoles = []
        self.Description = Description
        self.Announcement = Announcement
        self.RequestableRoleNames = RequestableRoleNames
        self.RequestableRoles = [] #Can be roles or members
        self.RandomNames = False
        for i in SpectatorRoleNames:
            self.SpectatorRoles.append(discord.utils.get(guild.roles, name=i))
        for i in TribeRoleNames:
            self.TribeRoles.append(discord.utils.get(guild.roles, name=i))
        for i in RequestableRoleNames:
            self.RequestableRoles.append(discord.utils.get(guild.roles, name=i))
    
    def reload(self, guild):
        self.guild = guild
        self.guildID = guild.id
        self.SpectatorRoles = [discord.utils.get(guild.roles, name=i) for i in self.SpectatorRoleNames]
        self.TribeRoles = [discord.utils.get(guild.roles, name=i) for i in self.TribeRoleNames]
        self.RequestableRoles = [discord.utils.get(guild.roles, name=i) for i in self.RequestableRoleNames]
        
    def jsondict(self):
        return {'guildID':self.guildID, 'Announcement':self.Announcement, 'RequestableRoleNames':self.RequestableRoleNames, 'Episode':self.Episode, 'SpectatorRoleNames':self.SpectatorRoleNames, 'Description':self.Description, 'AllianceCategoryName':self.AllianceCategoryName, 'TribeRoleNames':self.TribeRoleNames, 'RequestRoleMode':self.RequestRoleMode, 'RandomNames':self.RandomNames}
            
    def update(self, SpectatorRoleNames = None, TribeRoleNames = None, Episode = None, AllianceCategoryName = None, Description = None, RequestableRoleNames = None, Announcement = None):
        if not SpectatorRoleNames == None:
            #print(SpectatorRoleNames)
            self.SpectatorRoleNames = SpectatorRoleNames
            self.SpectatorRoles = []
            for i in SpectatorRoleNames:
                #print(i)
                self.SpectatorRoles.append(discord.utils.get(self.guild.roles, name=i))
                #print(self.SpectatorRoles[-1])
        if not TribeRoleNames == None:
            self.TribeRoleNames = TribeRoleNames
            self.TribeRoles = []
            for i in TribeRoleNames:
                self.TribeRoles.append(discord.utils.get(self.guild.roles, name=i))
        if not RequestableRoleNames == None:
            self.RequestableRoleNames = RequestableRoleNames
            self.RequestableRoles = []
            if self.RequestRoleMode:
                for i in RequestableRoleNames:
                    self.RequestableRoles.append(discord.utils.get(self.guild.roles, name=i))
            else:
                for i in RequestableRoleNames:
                    self.RequestableRoles.append(self.guild.get_member_named(i))
        if not Episode == None:
            self.Episode = Episode
        if not AllianceCategoryName == None:
            self.AllianceCategoryName = AllianceCategoryName
            self.AllianceCategory = discord.utils.get(self.guild.categories, name=AllianceCategoryName)
        if not Description == None:
            self.Description = Description
        if not Announcement == None:
            self.Announcement = Announcement
        
def setup(bot):
    for guild in bot.guilds:
        orgs.update({str(guild.id):org(guild)})     
    file = open('orgs.json', 'r')
    orgsdict = {}
    try:
        orgsdict.update(json.load(file))
        file.close()
    except:
        file.close()
    #print(orgsdict)
    for k in orgsdict.keys():
        t = orgsdict[k]
        #print(t)
        orgs[k].update(SpectatorRoleNames = t['SpectatorRoleNames'], Episode = t['Episode'], Description = t['Description'], AllianceCategoryName = t['AllianceCategoryName'], TribeRoleNames = t['TribeRoleNames'], RequestableRoleNames = t['RequestableRoleNames'], Announcement = t['Announcement'])
        orgs[k].RequestRoleMode = t['RequestRoleMode']
        orgs[k].RandomNames = t['RandomNames']
def write():
    file = open('orgs.json', 'w')
    orgsdict = {k:orgs[k].jsondict() for k in orgs.keys()}
    json.dump(orgsdict, file)
    file.close()
    
def addGuild(Guild):
    orgs.update({str(Guild.id):org(Guild)})
    
def removeGuild(Guild):
    return orgs.pop(str(Guild.id))

async def ORGRespond(messagearray, message):
    orgs[str(message.guild.id)].reload(message.guild)
    if messagearray[1].lower() == "alliance":
        await AllianceResponse(messagearray, message)
    if messagearray[1].lower() == "write" and botadmin(message.author):
        write()
    if messagearray[1].lower() == "settings" and message.author.guild_permissions.administrator:
        t = orgs[str(message.guild.id)]
        a = 'Spectator roles:  '
        for i in t.SpectatorRoleNames:
            a += i + ', '
        a = a[:-2] + '\n'
        b = 'Tribe roles:  '
        for i in t.TribeRoleNames:
            b += i + ', '
        a += b[:-2] + '\n'
        b = 'Requestable roles:  '
        for i in t.RequestableRoleNames:        
            b += i + ', '
        a += b[:-2] + '\n'
        try:
            a += 'Episode: ' + t.Episode 
        except:
            a += 'Episode: none'
        try:  
            a += '\nDescription: ' + t.Description 
        except:
            a += '\nDescription: none'
        try:
            a += '\nAlliance Category: ' + t.AllianceCategoryName
        except:
            a += '\nAlliance Category: none'
        try:
            a += '\nAnnouncement: ' + t.Announcement
        except:
            a += '\nAnnouncement: none'
        a += '\nRequest Mode: ' + ('discord usernames', 'individual roles')[int(t.RequestRoleMode)]
        a += '\nRandom names: ' + ('disabled', 'enabled')[int(t.RandomNames)]
        await message.channel.send(a)
    if messagearray[1] == "Dict" and botadmin(message.author):
        await message.channel.send(orgs[str(message.guild.id)].__dict__)
        #print(orgs[str(message.guild.id)].jsondict())
        
    mentions = message.role_mentions
    
    if messagearray[1].lower() == "tribes" and message.author.guild_permissions.administrator:
        if len(mentions) > 0:#mention every role to be assigned
            orgs[str(message.guild.id)].update(TribeRoleNames = [i.name for i in mentions])#there's redundancy in passing the names rather than the roles and than later getting the roles again from those names, but I don't want to rewrite stuff here.
            if None in orgs[str(message.guild.id)].TribeRoles:
                await message.channel.send('The tribe names were entered, but at least one name was not matched with a role. You should check if all the role names were spelled and capitalized correctly.')
                #This shouldn't be possible but I'll leave it for if there's something unexpected
            else:
                await message.channel.send('The tribes were successfully entered.')
        else:#type out the name of every role to be assigned
            orgs[str(message.guild.id)].update(TribeRoleNames = [i for i in messagearray[2:]])
            if None in orgs[str(message.guild.id)].TribeRoles:
                await message.channel.send('The tribe names were entered, but at least one name was not matched with a role. You should check if all the role names were spelled and capitalized correctly.')
            else:
                await message.channel.send('The tribes were successfully entered.')
                
    if messagearray[1].lower() == "requestmode" and message.author.guild_permissions.administrator:
        mime = orgs[str(message.guild.id)]
        mime.RequestRoleMode = not mime.RequestRoleMode
        await message.channel.send('The request mode is ' + ('discord usernames', 'individual roles')[int(mime.RequestRoleMode)])
    
    if messagearray[1].lower() == "randomnames" and message.author.guild_permissions.administrator:
        mime = orgs[str(message.guild.id)]
        mime.RandomNames = not mime.RandomNames
        await message.channel.send('Random names are now ' + ('disabled', 'enabled')[int(mime.RandomNames)])
        
    if messagearray[1].lower() == "requestables" and message.author.guild_permissions.administrator:
        if len(mentions) > 0:#mention every role to be assigned
            orgs[str(message.guild.id)].update(RequestableRoleNames = [i.name for i in mentions])#there's redundancy in passing the names rather than the roles and than later getting the roles again from those names, but I don't want to rewrite stuff here.
            if None in orgs[str(message.guild.id)].RequestableRole:
                await message.channel.send('The requestable names were entered, but at least one name was not matched with a role. You should check if all the role names were spelled and capitalized correctly.')
                #This shouldn't be possible but I'll leave it for if there's something unexpected
            else:
                await message.channel.send('The individual names were successfully entered.')
        else:
            orgs[str(message.guild.id)].update(RequestableRoleNames = [i for i in messagearray[2:]])
            if None in orgs[str(message.guild.id)].RequestableRoles:
                await message.channel.send('The requestable names were entered, but at least one name was not matched with a role. You should check if all the role names were spelled and capitalized correctly.')
            else:
                await message.channel.send('The individual names were successfully entered.')
                
    if messagearray[1].lower() == "specs" and message.author.guild_permissions.administrator:
        if len(mentions) > 0:#mention every role to be assigned
            orgs[str(message.guild.id)].update(SpectatorRoleNames = [i.name for i in mentions])#there's redundancy in passing the names rather than the roles and than later getting the roles again from those names, but I don't want to rewrite stuff here.
            if None in orgs[str(message.guild.id)].SpectatorRole:
                await message.channel.send('The spectator role names were entered, but at least one name was not matched with a role. You should check if all the role names were spelled and capitalized correctly.')
                #This shouldn't be possible but I'll leave it for if there's something unexpected
            else:
                await message.channel.send('The spectator roles were successfully entered.')
        else:
            orgs[str(message.guild.id)].update(SpectatorRoleNames = [i for i in messagearray[2:]])
            if None in orgs[str(message.guild.id)].SpectatorRoles:
                await message.channel.send('The spectator role names were entered, but at least one name was not matched with a role. You should check if all the role names were spelled and capitalized correctly.')
            else:
                await message.channel.send('The spectator roles were successfully entered.')
            
    if messagearray[1].lower() == "alliancecategory" and message.author.guild_permissions.administrator:
        orgs[str(message.guild.id)].update(AllianceCategoryName = messagearray[2])
        if None == orgs[str(message.guild.id)].AllianceCategory:
            await message.channel.send('The alliance category name was entered, but no category could be matched to it. You should check if the category name was spelled and capitalized correctly.')
        else:
            await message.channel.send('The category name was successfully entered.')
            
    if messagearray[1].lower() == "episode" and message.author.guild_permissions.administrator:
        orgs[str(message.guild.id)].update(Episode = messagearray[2])
        await message.channel.send('The episode was entered.')
        
    if messagearray[1].lower() == "description" and message.author.guild_permissions.administrator:
        s = ""
        for i in messagearray[2:]:
            s += i + ' '
        orgs[str(message.guild.id)].update(Description = s[:-1])
        if getChannelTopic(message, s[:-1], [''], '', '', '') == None:
            await message.channel.send('The description was entered, but it doesn\'t form a valid description.')
        else:
            await message.channel.send('The description was entered.')
            
    if messagearray[1].lower() == "announcement" and message.author.guild_permissions.administrator:
        s = ""
        for i in messagearray[2:]:
            s += i + ' '
        orgs[str(message.guild.id)].update(Announcement = s[:-1])
        if getAnnouncement(message, s[:-1], [''], '', '', '', message.guild.default_role, message.guild.default_role) == None:
            await message.channel.send('The announcement was entered, but it doesn\'t form a valid announcement.')
        else:
            await message.channel.send('The announcement was entered.')
            
    elif messagearray[1].lower() == "setup":#this is defunct, would not recommend using it
    #basically, you use the command, followed by a tribe marked with !, then the contestants in that tribe, then another tribe name, then the contestants in that tribe, ect, at the end use S!(specname) to mark spec roles
    #This also makes the roles and stuff
    #I don't fully remember what this does so if you for some reason try to use it I would recommend testing it
        if message.author.guild_permissions.administrator: #set up confs and submissions
            await SetupResponse(messagearray, message)
        else:
            await message.channel.send("You must be a host to use that.")
        
async def AllianceResponse(messagearray, message):#message does the same as ctx here, messagearray is the parsed message content by spaces
    t = orgs[str(message.guild.id)] #holds server-specific alliance making information
    global wordlist
    if t.RequestRoleMode: #alliance making based on individual roles
        Requester = None#first check if author is a contestant; then the author becomes the requester
        Auth = False
        for i in t.TribeRoles: #the server-specific roles for 
            if i in message.author.roles:
                for authorrole in message.author.roles:
                    if ((len(authorrole.members) == 1 and len(t.RequestableRoles) == 0) or (not len(t.RequestableRoles) == 0 and authorrole in t.RequestableRoles)):
                        messagearray.insert(2, authorrole.name)#now that I'm looking at it this seems like a real strange way of doing things
                        Auth = True
                Requester = message.author
        if message.author.guild_permissions.administrator:#check if author is an admin; the first listed alliance member becomes the requester
            Auth = True
            Found = False
            for guildrole in message.guild.roles:
                if guildrole.name.lower() == messagearray[2].lower():
                    for membersearch in message.guild.members:
                        if guildrole in membersearch.roles:#idk what I was doing with these loops, a lot of this can probably be replaced with the discord get function
                            Requester = membersearch
                            Found = True
                            break
            if not Found:
                await message.channel.send("The requester's name was incorrect.")
                return
        if Auth == True:
            AllianceMemberRoles = []
            ThisTribeRole = None
            for Tribe in t.TribeRoles:
                for AuthorRole in Requester.roles:
                    if Tribe == AuthorRole:
                        ThisTribeRole = Tribe
            for requestname in messagearray[2:]:
                found = False
                for guildrole in t.guild.roles:
                    if guildrole.name.lower() == requestname.lower() and ((len(guildrole.members) == 1 and len(t.RequestableRoles) == 0) or (not len(t.RequestableRoles) == 0 and guildrole in t.RequestableRoles)):
                        found = True
                        if not guildrole in AllianceMemberRoles:
                            AllianceMemberRoles.append(guildrole)
                if not found:
                    await message.channel.send("The name " + requestname + ' was incorrect.')
                    return
            for OtherMemberRoles in AllianceMemberRoles[1:]:
                for membersearch in t.guild.members:
                    if OtherMemberRoles in membersearch.roles:
                        if not ThisTribeRole in membersearch.roles:
                            await message.channel.send("One of the alliance members is not on the requester's tribe.")
                            return
            if len(AllianceMemberRoles) < 2:
                await message.channel.send("There were not enough alliance members to complete the request.")
                return
            if len(AllianceMemberRoles) >= len(ThisTribeRole.members):
                await message.channel.send("You cannot make an alliance with the entire tribe.")
                return
            ChannelName = ""
            ChannelTopic = ""
            if t.RandomNames:
                for i in range(r.choice([2, 3, 3, 4, 4, 5, 6])):
                    word = r.choice(wordlist)
                    ChannelName += word + "-"
            else:
                for role in AllianceMemberRoles:
                    ChannelName += role.name.lower() + "-"
            ChannelName = ChannelName[:-1]
            try:
                ChannelTopic = getChannelTopic(message, t.Description, [a.name for a in AllianceMemberRoles], ThisTribeRole.name, Requester.name, t.Episode)
            except:
                ChannelTopic = '-'
            Perms = {}
            for role in AllianceMemberRoles:
                Perms.update({role:discord.PermissionOverwrite(read_messages = True, send_messages = True, read_message_history=True)})
            for role in t.SpectatorRoles:
                Perms.update({role:discord.PermissionOverwrite(read_messages = True, send_messages = False, read_message_history=True)})
            Perms.update({message.guild.default_role:discord.PermissionOverwrite(read_messages=False)})
            channel = await message.guild.create_text_channel(ChannelName, overwrites=Perms, category=t.AllianceCategory, topic=ChannelTopic) #SpectatorPerms
            await channel.set_permissions(message.guild.default_role, read_messages=False)#I did this twice out of paranoia of everyone being able to see an alliance
            try:
                await channel.send(getAnnouncement(message, t.Announcement, [a.name for a in AllianceMemberRoles], ThisTribeRole.name, Requester.name, t.Episode, ThisTribeRole, Requester))
                #will throw an error if there is no announcement or the announcement is badly formatted
            except:
                pass
        else:
            await message.channel.send("You must be a host or a contestant to use that.")
    else:#function based on discord username
        AllianceMembers = []
        Auth = False
        Requester = None
        for i in t.TribeRoles:
            if i in message.author.roles and ((len(t.RequestableRoles) == 0) or (not len(t.RequestableRoles) == 0 and Requester in t.RequestableRoles)):
                Requester = message.author
                Auth = True
                AllianceMembers.append(Requester)
        if message.author.guild_permissions.administrator:
            Auth = True
            Requester = t.guild.get_member_named(messagearray[2].capitalize())
            if Requester == None:
                await message.channel.send("The requester's name was incorrect.")
                return
        if Auth == True:
            for Tribe in t.TribeRoles:
                if Tribe in Requester.roles:
                    ThisTribeRole = Tribe
            for name in messagearray[2:]:
                member = t.guild.get_member_named(name)
                if member == None:
                    await message.channel.send("The name " + name + ' was incorrect.')
                    return
                if not member in AllianceMembers:
                    AllianceMembers.append(member)
            print(AllianceMembers)
            for OtherMember in AllianceMembers[1:]:
                if not ThisTribeRole in OtherMember.roles:
                    await message.channel.send("One of the alliance members is not on the requester's tribe.")
                    return
            if len(AllianceMembers) < 2:
                await message.channel.send("There were not enough alliance members to complete the request.")
                return
            if len(AllianceMembers) >= len(ThisTribeRole.members):
                await message.channel.send("You cannot make an alliance with the entire tribe.")
                return
            channelname = ""
            ChannelTopic = ""
            if t.RandomNames:
                for i in range(r.choice([2, 3, 3, 4, 4, 5, 6])):
                    word = r.choice(wordlist)
                    ChannelName += word + "-"
            else:
                for member in AllianceMembers:
                    channelname += member.name.lower() + "-"
            channelname = channelname[:-1]
            try:
                ChannelTopic = getChannelTopic(message, t.Description, [a.name for a in AllianceMembers], ThisTribeRole.name, Requester.name, t.Episode)
            except:
                ChannelTopic = '-'
            Perms = {}
            for member in AllianceMembers:
                print(str(Comms.checkUser(member, message.guild)))
                if Comms.checkUser(member, message.guild) is False:
                    Perms.update({member:discord.PermissionOverwrite(read_messages = True, send_messages = False, read_message_history=True, add_reactions = False)})
                else:
                    Perms.update({member:discord.PermissionOverwrite(read_messages = True, send_messages = True, read_message_history=True)})
            for role in t.SpectatorRoles:
                Perms.update({role:discord.PermissionOverwrite(read_messages = True, send_messages = False, read_message_history=True)})
            Perms.update({message.guild.default_role:discord.PermissionOverwrite(read_messages=False)})
            try:
                channel = await message.guild.create_text_channel(channelname, overwrites=Perms, category=t.AllianceCategory, topic=ChannelTopic)
            except:
                pass
            await channel.set_permissions(message.guild.default_role, read_messages=False)
            try:
                await channel.send(getAnnouncement(message, t.Announcement, [a.name for a in AllianceMembers], ThisTribeRole.name, Requester.name, t.Episode, ThisTribeRole, Requester))
            except:
                pass
        else:
            await message.channel.send("You must be a host or a contestant to use that.")
                
def getChannelTopic(m, d, a, t, r, e):
    vals = ['members', 'requester', 'episode', 'tribe', 'date']
    s = ''
    add = False
    out = ''
    for j in range(len(d)):
        i = d[j]
        if i == '{' and not add:
            add = True
        elif add and i == '}':
            add = False
            b = ''
            if s == vals[0]: 
                for k in a:
                    b += k + ', '
                out += b[:-2]
            elif s == vals[1]: 
                out += a[0]
            elif s == vals[2]: 
                out += e
            elif s == vals[3]: 
                out += t
            elif s == vals[4]: 
                out += str(m.created_at.now(tz=datetime.timezone(-datetime.timedelta(hours=4)))).split()[0]
            else:
                return None
            s = ''
        elif i == '}' or i == '{': 
            return None
        elif add:
            s += i
        else:
            out += i
    return out

def getAnnouncement(m, d, a, t, r, e, tr, rr):
    vals = ['members', 'requester', 'episode', 'tribe', 'requesterping', 'tribeping', 'date']
    s = ''
    add = False
    out = ''
    for j in range(len(d)):
        i = d[j]
        if i == '{' and not add:
            add = True
        elif add and i == '}':
            add = False
            b = ''
            if s == vals[0]: 
                for k in a:
                    b += k + ', '
                out += b[:-2]
            elif s == vals[1]: 
                out += a[0]
            elif s == vals[2]: 
                out += e
            elif s == vals[3]: 
                out += t
            elif s == vals[4]:
                out += rr.mention
            elif s == vals[5]:
                out += tr.mention
            elif s == vals[6]: 
                out += str(m.created_at.now(tz=datetime.timezone(-datetime.timedelta(hours=4))).strftime('%m/%d/%Y')).split()[0]
            else:
                return None
            s = ''
        elif i == '}' or i == '{': 
            return None
        elif add:
            s += i
        else:
            out += i
    return out

async def SetupResponse(messagearray, message):#defunct
    tribelist = []
    SpectatorRole = None
    for name in messagearray[2:]:
        if(name[0] == '!'):
            tribelist.append([name[1:]])
        elif(name.startswith('S!')):
            SpectatorRole = discord.utils.get(message.guild.roles, name = name[2:])
        else:
            tribelist[-1].append(name)
    tribecategories = []  
    for tribe in tribelist:
        thistribecategory = await message.guild.create_category(tribe[0])
        tribecategories.append(thistribecategory)
        for castaway in tribe[1:]:
            thisrole = await message.guild.create_role(name = castaway)
            newchannel = await message.guild.create_text_channel(castaway, category=thistribecategory)
            await newchannel.set_permissions(SpectatorRole, read_messages=True, send_messages=False, read_message_history=True)
            await newchannel.set_permissions(thisrole, read_messages=True, send_messages=True, read_message_history=True)
            await newchannel.set_permissions(message.guild.default_role, read_messages=False)
            await newchannel.send('Welcome to your confessionals! Feel free to share your thoughts with spectators here.')
            newchannel = await message.guild.create_text_channel(castaway + "-submissions", category=thistribecategory, overwrites = {message.guild.default_role: discord.PermissionOverwrite(read_messages=False)})
            await newchannel.set_permissions(thisrole, read_messages=True, send_messages=True, read_message_history=True)
            await newchannel.send('Welcome to your submissions channel! This channel is for submitting for challenges and votes. You can also share things with hosts that you don\'t want specs to see.')