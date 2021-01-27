import discord

async def HelpRespond(messagearray, message):
    m = ''
    if len(messagearray) == 1:#default
        m += '**Report**\n'
        m += 'Report a problem with the bot. This is useful if the maker of this bot is not in the server.\n'
        m += '**Link**\n'
        m += 'Posts a link to invite this bot to another server.\n'
        m += '**Changes**\n'
        m += 'See recent changes to the bot, along with the date of changes.\n'
        m += '**--Subcategories--** (use H!Help {Subcategory} to see more, i.e. H!Help Battle)\n'
        m += '**ORG**\n'
        m += 'Contains commands related to running ORGs, most notably the alliance maker function.\n'
        m += '**Battle**\n'
        m += 'Contains commands related to the dungeon battle game, which is a text-based battle royale.\n'
        m += '**Utils**\n'
        m += 'Contains utility commands, most notably the permissions command that can be used to quickly set or change permissions for a channel.\n'
        m += '**Clock**\n'
        m += 'Contains details of a timer, similar to a chess clock, that counts down the time for different teams.\n'
        m += '**Coordination**\n'
        m += 'Contains details of the coordination game, in which everyone with a particular role must work together to complete tasks before they expire.\n'
        
    else:
        if messagearray[1] == 'Utils':
            if len(messagearray) == 2:
                m += 'Preface these commands with `H!Utils` i.e. `H!Utils Ping`\n'
                m += '**Ping**\n'
                m += 'The bot will give a simple response, confirming that it is online and responding to commands.\n'
                m += '**Perm**\n'
                m += 'Sets roles to have the permission set stated in the channel the message was sent in. Permissions can be:\n'
                m += 'Read - The role(s) can read but not send messages in the channel.\n'
                m += 'Write - The role(s) can read and send messages in the channel.\n'
                m += 'Hide - The channel is specifically hidden from the role(s).\n'
                m += 'Remove - The role(s) is given no particular permissions in the channel. Any permissions it did have are removed.\n'
                m += 'Example: `H!Utils Perm Read Spectator Castaway`'
        elif messagearray[1] == 'ORG':
            if len(messagearray) == 2:
                m += '**--Setup--**\n'
                m += 'The alliance maker allows players to make alliances with other players automatically. The following setup commands are needed for it to work in a server.\n'
                m += '**Tribes**\n'
                m += 'H!ORG Tribes (tribe role name 1) (tribe role name 2) (ect): sets the tribe roles-the people with these roles will be able to make alliances with other people with the role. i.e. `H!ORG Redville Bluetown`\n'
                m += '**Specs**\n'
                m += 'H!ORG Specs (spec role name 1) (spec role name 2) (ect): sets the roles that can see alliances (but can’t speak in them)\n'
                m += '**Alliancecategory**\n'
                m += 'H!ORG Alliancecategory (Alliance category name): sets the category for alliances to be made in\n'
                m += '**Episode**\n'
                m += 'H!ORG Episode (episode number or title): sets the episode. This is only important for channel descriptions\n'
                m += '**Description**\n'
                m += 'H!ORG Description (description): sets the description to be set for alliances (in the channel topic). This string can be customized with {members}, {requester}, {episode}, {date}, and {tribe}-the corresponding value will be inserted in the string. Example: `H!ORG Description {members} | Requested by {requester} | Made on {date} | {tribe}`\n'
                await message.channel.send(m)
                m = '**RequestMode**\n'
                m += 'H!ORG RequestMode: Sets whether requests are based on individual roles (The default) or discord usernames and discriminators (this will set it to the opposite of what it is now).\n'
                m += '**Requestables**\n'
                m += 'H!ORG Requestables (requestable role name 1) (requestable role name 2) ect. Specifies the roles that people can request for their alliance (i.e. individual roles you give to each player). This role is also automatically added to an alliance if the requester has it, so nobody should have more than one of these roles. If no roles are specified (as is the default), all roles with only one member will be treated as requestable. This is not necessary under the discord username mode.\n'
                m += '**Announcement**\n'
                m += 'H!ORG Announcement: Sets the announcement-the message the hosting bot sends in the channel when it is first made, with insertion possible like with the description. Two more arguments are possible-{tribeping} and {requesterping}\n'
                m += '**--Others--**\n'
                m += '**Settings**\n'
                m += 'Shows the settings for the alliance maker in the current server.\n'
                m += '**Alliance**\n'
                m += 'This is the command for requesting an alliance; it will make an alliance according to the settings as described above. If the alliance maker mode is roles, use the name of individual roles given to each alliance member; Otherwise, put the discord usernames of the alliance members (in both instances, seperated by spaces). Hosts can also request alliances, with the requesting contestant\'s name first. i.e. `H!ORG Alliance Jerry Tim Scot` for an alliance of Ian, Jerry, Tim, and Scot if the command was sent by Ian\n'
        elif messagearray[1] == 'Clock':
            if len(messagearray) == 2:
                m += '**(No command)**\n'
                m += 'To start a countdown clock, enter `H!Clock (number) (role1) (role2) ect.` The number represents how much time, in seconds, to put on the clock, while the roles describe the teams that can operate the clock.\n'
                m += 'The clock works like a chess timer, wherein anyone with the stated role can \'hit\' the timer while it is their turn, stopping their team\'s time and starting the time of the next team.\n'
                m += 'The clock will stop when the Stop command is used or when a team runs out of time.\n'
                m += 'You can enter no roles to have the clock only react to the message poster.\n'
                m += '**Turn**\n'
                m += 'If used by someone with the role that the timer is currently on, this will stop their time from counting down and start the next roles\'s. If there is only one role it stops the time.\n'
                m += '**Stop**\n'
                m += 'Stops the timer altogether.\n'
                m += 'Example: `H!Clock 180 team1 team2` will start a 3-minute clock for team1 and team2. team1 and team2 need to be roles in this case.'
        elif messagearray[1] == 'Battle':
            if len(messagearray) == 2:
                m += 'Use `H!Help Battle {command}` to see more about these commands, i.e. `H!Help Battle Move`.\n'
                m += 'Use `H!Help Battle Items` to see item descriptions\n'
                m += '**--Game Control-- (only usable by admins)**\n'
                m += '**Setup**\n'
                m += 'Sets up a game and creates the rooms. Always use this first when starting a match.\n'
                m += '**Spawn**\n'
                m += 'Spawns the given items in the current battle.\n'
                m += '**Register**\n'
                m += 'Registers the given users as players and places them in a room.\n'
                m += '**RegisterAt**\n'
                m += 'Registers the given users as players and places them in specified locations.\n'
                m += '**CustomMessage**\n'
                m += 'Allows players to find the following message when they search the room.\n'
                m += '**End**\n'
                m += 'Ends the game and deletes channels and categories associated with it.\n'
                m += '**Poison**\n'
                m += 'Starts poison spreading and sets how long it will take before poison spreads further.\n'
                m += '**PoisonSpeed**\n'
                m += 'Modifies how long it takes for poison to deal damage.\n'
                m += '**PoisonDamage**\n'
                m += 'Modifies how much damage poison deals.\n'
                m += '**Give**\n'
                m += 'Gives items directly to players.\n'
                m += '**Remove**\n'
                m += 'Removes the mentioned players from the battle.\n'
                m += '**Recording**\n'
                m += 'Starts a recording of the current battle.\n'
                m += '**StopRecording**\n'
                m += 'Stops the recording of the current battle.\n'
                m += '**--Game Commands-- (only usable by players in their battle channel)**\n'
                m += '**Move**\n'
                m += 'Attempts to move in the given direction.\n'
                m += '**Scout**\n'
                m += 'Shows which directions have walls for the current room.\n'
                m += '**Search**\n'
                m += 'Gives a list of items in the current room.\n'
                m += '**Get**\n'
                m += 'Puts the given item in the player\'s inventory.\n'
                m += '**Inventory**\n'
                m += 'Shows the items currently in the player\'s inventory.\n'
                m += '**Drop**\n'
                m += 'Drops the given item in the player\'s inventory. The item becomes available to get in the player\'s room.\n'
                m += '**Attack**\n'
                m += 'Try to attack another player with a weapon or fist. The attack can be melee or ranged depending on the weapon used.\n'
                m += '**Use**\n'
                m += 'Use the given (non-weapon) item to gain it\'s benefits.\n'
                m += '**Status**\n'
                m += 'Shows the player\'s health and any stat boosts they received from items.\n'
                m += '**Map**\n'
                m += 'Shows a map of the current dungeon if the user has the option enabled.\n'
            else:
                if messagearray[2] == 'Setup':
                    m += 'This will be the first command you use to start a battle. The first 2 arguments are required-they are the width and height of the dungeon. An optional third argument will determine how many walls there are-higher numbers will produce less walls. Finally, you can list all roles you want to be able to spectate the battle.\n'
                    m += 'Example: `H!Battle Setup 8 6 10 Spectator` will make an 8-by-6 dungeon with relatively few walls that is visible to people with the spectator role.'
                elif messagearray[2] == 'Spawn':
                    m += 'This command spawns items into the current battle (it must be used after the setup command). You can spawn items by saying the name of the item as an argument and the number of items to spawn as the next argument.\n'
                    m += 'Example: `H!Battle Spawn Blaster 10 Knife 20 Steroids 3` will spawn 10 blasters, 20 knives and 3 steroids.'
                elif messagearray[2] == 'Register':
                    m += 'This command will register the players mentioned after into the game.\n'
                    m += 'Example: `H!Battle Register @Quinn`'
                elif messagearray[2] == 'RegisterAt':
                    m += 'This command takes any number of users (pings) and twice as many integers as arguments. Each user will be registered as a player and assigned to the room with corresponding coordinates.\n'
                    m += 'Example: `H!Battle Register @Quinn 6 3 @OverratedFireLizard 2 5` will register Quinn at room 6-3 and OverratedFireLizard at room 2-5.\n'
                elif messagearray[2] == 'End':
                    m += 'Ends the current game and deletes related categories and channels. This must be used before starting a new battle, and takes no arguments.\n'
                elif messagearray[2] == 'Poison':
                    m += 'This command starts poison spread. The arguments for this command are integers seperated by spaces, representing how long it will take poison to spread each round, in seconds. Poison starts at the edge of the map and moves inwards each round. \n For example, `H!Battle Poison 300 240 180` will spread poison to the outermost rooms after 5 minutes, move 1 layer in after 4 minutes, and finally will move in another layer after 3 more minutes.\n'
                elif messagearray[2] == 'PoisonDamage':
                    m += 'Sets how much damage players take from poisoned rooms (for the current battle only). By default they will take damage equal to the number of times poison has spread (making poison more dangerous over time if there are multiple rounds of poison). i.e. `H!Battle PoisonDamage 5` for poison to deal 5 damage.\n'
                elif messagearray[2] == 'PoisonSpeed':
                    m += 'Sets how long (in seconds) it takes players in a poisoned room to take damage. 15 by default. The time a player spent in poison does not reset if they leave a poisoned room. i.e. `H!Battle Poison 10` for damage to occur every 10 seconds.\n'
                elif messagearray[2] == 'Give':
                    m += 'Gives the mention players the stated items in the stated amounts. i.e. `H!Battle Give @player1 @player2 Sword 10 Shield 10` gives player1 and player2 10 swords and 10 shields.\n'
                elif messagearray[2] == 'Remove':
                    m += 'Removes the mentioned players from the battle. i.e. `H!Battle Remove @player1 @player2` to remove player1 and player2\n'
                elif messagearray[2] == 'CustomMessage':
                    m += 'Sets a custom message for the room that players will see when they search it. i.e. `H!Battle CustomMessage there is a secret in this room.`\n'
                elif messagearray[2] == 'Move':
                    m += 'This command moves the player (author) in the stated direction if there is not a wall/boundry in the way. Directions can be north/south/east/west (not case sensitive) or just the first letter of those directions.\n'
                    m += 'Example: `H!Move n` to move north.'
                elif messagearray[2] == 'Search':
                    m += 'This command shows a list of all items in the room the player is in. It takes no arguments.\n'
                elif messagearray[2] == 'Scout':
                    m += 'This command tells you which directions have walls that will prevent you from moving, for the room you are in. The dungeon boundry is not included. It takes no arguments.\n'
                elif messagearray[2] == 'Get':
                    m += 'This command will move the stated item in the room to the player\'s inventory. A second argument can be added to express which item in the room\'s item list you want to take if there are multiple copies in the same room.\n'
                    m += 'Example: `H!Battle Get Blaster 3` will pick up the third blaster in the room.'
                elif messagearray[2] == 'Inventory':
                    m += 'This command shows every item in the player\'s inventory, along how many uses they have left. It takes no arguments.\n'
                elif messagearray[2] == 'Drop':
                    m += 'This command drops the stated item, putting it in the player\'s room\'s item list. There is no inventory limit so this command will only rarely need to be used in team games. Like the get command you can specify which item to drop if there are multiple copies.\n'
                    m += 'Example: `H!Battle Drop Vest 2` will drop the second vest in the inventory list.'
                elif messagearray[2] == 'Attack':
                    m += 'This command is used to attack. Attacks can be melee or ranged depending on which weapon is used. Fists, Knife, Machete, Sword, and Lightsaber are melee weapons, while Pistol, Musket, Rifle, and Blaster are ranged weapons. Fists can be used any time.\n'
                    m += 'When making a melee attack, mention the player you are attacking. They must be in your room. Example: `H!Battle Attack Sword @Quinn`.\n'
                    m += 'When making a ranged attack, state which direction you are shooting. Your shot will travel until it hits a wall, goes out of bounds, or enters a room with a player (dealing damage to them). Example: `H!Battle Attack Pistol n`.\n'
                elif messagearray[2] == 'Use':
                    m += 'Uses the stated item (non-weapons). Potion restores health while Scope, Shield, Vest, and Steroids increase one of your stats.\n'
                    m += 'Example: `H!Battle Use Potion` will restore 3 health and use up one use of your first potion.'
                elif messagearray[2] == 'Status':
                    m += 'Shows your health and any stat boosts you have received. This command takes no arguments.\n'
                if messagearray[2] == 'Recording':
                    m += 'This starts \"recording\" the current battle. It does this by saving a picture of the map-the same as is generated when an admin uses it-every second. This takes no arguments.\n'
                if messagearray[2] == 'StopRecording':
                    m += 'Stops the recording of the battle. Depending on the size of the folder with the map images, this command will produce a video, a zip folder, or nothing (requiring manual retrieval). This will probably produce a zip file most of the time.\n'
                    m += 'This takes one optional argument, a number representing the frames per second of the video.\n'
                if messagearray[2] == 'Map':
                    m += 'Produces a map of the dungeon. A player will need to get and use a map item first to use this command. Admins can use it regardless. For admins, the map will show the locations and health of all players in the dungeon.\n'
                elif messagearray[2] == 'Items':
                    m += '**Melee Weapons**:\n'
                    m += 'Knife: 6 uses, 2 damage\n'
                    m += 'Machete: 5 uses, 3 damage\n'
                    m += 'Sword: 4 uses, 4 damage\n'
                    m += 'Lightsaber: 3 uses, 6 damage\n'
                    m += '**Ranged Weapons**:\n'
                    m += 'Pistol: 8 uses, 1 damage\n'
                    m += 'Musket: 6 uses, 2 damage\n'
                    m += 'Rifle: 5 uses, 3 damage\n'
                    m += 'Blaster: 4 uses, 4 damage\n'
                    m += 'Bow: 6 uses, 1 damage\n'
                    m += 'Crossbow: 4 uses, 3 damage\n'
                    m += 'Bows and Crossbows are silent-they will not reveal your location to other players.\n'
                    m += '**Explosives**:\n'
                    m += 'Bomb: Explodes after an amount of time (5 seconds default), killing everyone in the room and causing the room to collapse (The room becomes surronded by walls on all sides). i.e. `H!Battle Attack Bomb 10` to have the bomb explode in 10 seconds in the current room.\n'
                    m += 'Rocket: Fire this like a ranged weapon, i.e. `H!Battle Attack Rocket s`. When it hits a wall, the dungeon boundry, or player, it explodes like the bomb.\n'
                    m += 'It is recommended you include drills in battles with explosives, or else players may end up being unable to reach each other.\n'
                    m += '**Stat-Boosting items**:\n'
                    m += 'These items either decrease damage from other player\'s attacks (melee or ranged) or increase the damage you deal with them. You can boost a stat up to 3 times, and damage cannot be reduced below 1.\n'
                    m += 'Shield: Decreases damage from melee attacks\n'
                    m += 'Vest: Decreases damage from ranged attacks\n'
                    m += 'Steroids: Increases melee damage\n'
                    m += 'Scope: Increases ranged attack\n'
                    m += '**Other items**:\n'
                    m += 'Potion: Has between 1-3 uses and heals 3 health each use.\n'
                    m += 'Berries: Single use, heals up to 14 health or deals up to 12 damage to the user.\n'
                    m += 'Drill: Removes a wall in the stated direction, i.e. `H!Battle Use Drill e` to destroy the east wall of the room.\n'
                    m += 'Compass: Shows you approximately where the other players are. Has 4 uses.\n'
                    m += 'Map: if you use this, you can use `H!Battle Map` to see a map of the dungeon.\n'
        if messagearray[1] == 'Coordination':
            if len(messagearray) == 2:
                m += 'In the game announcements channel, tasks will be posted periodically with increasing difficulty and frequency and decreasing time limits.\n'
                m += 'For example: `Enter t-w-b` in area 2. This means you should enter twb (without dashes) in the channel called area-2.\n'
                m += '**--Game Control-- (only usable by admins)**\n'
                m += 'Setup: sets up a coordination game with the given role, number of rooms, and spectator roles.\n'
                m += 'Example: `C!Coordination Setup 6 TribeA Spectator Jury` to create a coordination game with 6 rooms, with TribeA as players and Spectator and Jury as spectators.\n'
                m += 'Start: Starts the game.\n'
                m += 'End: Ends the game and deletes the associated channels.\n'
    await message.channel.send(m)
        
        