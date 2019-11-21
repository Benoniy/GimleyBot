'''
StockImageBot v2
Improved version of the previous StockImageBot
making use of a SQLite databse for managing servers, roles and users
'''

# ---[ Imports ]---
import discord
import sqlite3 as db
import os
import re
import random

client = discord.Client

# ---[ Bot Variables ]---
# Testing bot token
TOKEN = "NTU5ODk4NjI0MDg4MjExNDU2.D3u5fw.gVs5shbmR6_OysVkDnplpM1w3mk"
BOT_PREFIX = "{"
# These control messages printed to console
info = True
warnings = True


# ---[ DB Access Methods ]---
def dbSet(script):
    # TODO add sanitization
    # To be used with 'INSERT' and 'UPDATE' style commands
    connection = db.connect('bot2.db')
    cursor = connection.cursor()
    cursor.execute(script)
    connection.commit()
    connection.close()


def dbGet(script):
    # TODO add sanitization
    # To be used with 'SELECT' style commands
    connection = db.connect('bot2.db')
    cursor = connection.cursor()
    cursor.execute(script)
    # fetchall() returns a tuple of tuples
    get = cursor.fetchall()
    connection.close()
    return get


def dbBuild():
    # Should only be called when the bot is run for the first time
    connection = db.connect('bot2.db')
    cursor = connection.cursor()
    try:
        script = open("build.sql", "r").read()
        cursor.execute(script)
        connection.commit()
        connection.close()
    except IOError:
        print("ERROR: Unable read or find 'build.sql'. Exiting program!")
        connection.close()
        exit()


def xpUser(xp, user):
    # TODO give additional XP for using a bot command
    author_score = dbGet(
        "SELECT xp, userLevel FROM users WHERE userID={0} AND guildID={1};".format(user.id, user.guild))
    author_score = author_score[0]
    author_xp = author_score[0]
    author_level = author_score[1]
    author_xp += xp
    if author_xp >= 1000:
        author_level += 1
        author_xp -= 1000
    dbSet("UPDATE users SET xp={0}, userLevel={1} WHERE userID={2};".format(author_xp, author_level, user.id))


def dbUpdate():
    # Acts as integrity check to ensure data stored on db
    # matches that current bot information

    # Get db stored information
    db_guilds = dbGet("SELECT * FROM servers;")

    guild_ids = []
    # Compare Bot information to server information
    for row in db_guilds:
        guild_ids.append(row[0])

    # Loop through all servers bot is part of
    for current_guild in client.fetch_guilds():
        if current_guild.id not in guild_ids:
            # Database does not have a server the bot is registered with
            if warnings: print("WARNING: Database missing a server: {0} which bot is in.".format(current_guild.name))
            dbSet("INSERT INTO servers VALUES {0}, '{1}';".format(current_guild.id, current_guild.name))

        # Check stored server name matches current server id
        for guild in db_guilds:
            if guild[0] == current_guild.id:
                # ID match - now check name consistency
                if not guild[1].equals(current_guild.name):
                    if info: print("INFO: Updating server name for {0} in database.".format(current_guild.name))
                    dbSet("UPDATE servers SET guildName='{0}' WHERE guildID={1};".format(current_guild.id, current_guild.name))

        # Check roles in server
        db_roles = dbGet("SELECT * FROM roles WHERE guildID={0};".format(current_guild.id))
        role_ids = []
        for row in db_roles:
            role_ids.append(row[2])
        for role in current_guild.roles:
            if role.id not in role_ids:
                # Database does not have a role from server registered
                if warnings: print("WARNING: Database missing role: {0} from guild: {1}".format(role.name, current_guild.name))
                dbSet("INSERT INTO roles (roleID, guildID, roleType, roleRegex) VALUES ({0}, {1}, {2}, '{0}';".format(role.id, current_guild.id, 0, role.name))

        # Check users in server
        db_users = dbGet("SELECT * FROM users WHERE guildID={0};".format(current_guild.id))
        member_ids = []
        for row in db_users:
            member_ids.append(row[0])
        for member in current_guild.members:
            if member.id not in member_ids:
                # Database does not have a user from server registered
                if warnings: print("WARNING: Database missing user: {0} ({1}) from guild: {2}.".format(member.display_name, member.nick, current_guild.name))
                dbSet("INSERT INTO users (userID, guildID, xp, userLevel) VALUES ({0}, {1}, 0, 0);".format(member.id, current_guild.id))


# ---[ Bot Start-Up Code ]---
@client.event
async def on_ready():
    # Set Discord Status
    activity = discord.Game(" deporting Akif.")
    await client.change_presence(status=discord.Status.online, activity=activity, afk=False)
    if info: print("INFO: Dominatrix Bot now online.\n")


# ---[ Bot Event Code ]---
@client.event
async def on_member_join(member):
    # New member joined server
    if info: print("INFO: A new member has joined a server.")

    # Get roles from server for when a new user joins
    db_roles = dbGet("SELECT ID FROM roles WHERE guildID={0} AND type=4;".format(member.guild.id))
    for role in db_roles:
        try:
            await member.add_roles(member.guild.get_role(role[0]), reason="Newly joined", atomic=True)
        except discord.Forbidden:
            if warnings: print("WARNING: Don't have permission to give roles to new member.")
        except discord.HTTPException:
            if warnings: print("WARNING: An HTTP Exception was thrown. Unable to give new member roles.")

    # Add user to the database
    # VALUES: userID, guildID, xp, userLevel
    dbSet("INSERT INTO users (userID, guildID, xp, userLevel) VALUES ({0}, {1}, 0, 0);".format(member.id, member.guild.id))


@client.event
async def on_message(message):
    # Simple setup
    author = message.author
    channel = message.channel
    args = message.split(' ')

    # Message recieved - bot should only reply to users, not other bots
    if author != client.user and BOT_PREFIX in message.content:
        # Since bot prefix was used, check if fits any of the commands
        if info: print("INFO: Message recieved: {0}".format(message))
        xpUser(20, author)

        if re.search("^["+BOT_PREFIX+"]\s", message):
            # There is a space between bot-prefix and command
            del args[0] # Remove }
            del args[1] # Remove command
        else:
            del args[0] # Remove }command

        # Now check message against commands
        # A simple status check command
        if re.search("^["+BOT_PREFIX+"]\s?(STATUS|status|Status|State|state)", message) is not None:
            if info: print("INFO: 'status' command received.")
            await channel.send("Dominatrix Bot 2.0 is Online.")

        # Rolls a dice
        elif re.search("^["+BOT_PREFIX+"]\s?(ROLL|roll|Roll|dice)", message) is not None:
            if info: print("INFO: 'roll' command received.")
            await roll_dice(message, args)

        # Flips a coin
        elif re.search("^["+BOT_PREFIX+"]\s?(FLIP|flip|Flip)(_|\s|-)?(COIN|Coin|coin)?", message) is not None:
            if info: print("INFO: 'flip' command received.")
            await flip_coin(message)

        # Returns list of modpacks & links to get them
        elif re.search("^["+BOT_PREFIX+"]\s?(MODPACKS?|modpacks?|Modpacks?)", message) is not None:
            if info: print("INFO: 'modpacks' command received.")
            #TODO modpacks command

        # Add a modpack to list
        elif re.search("^[" + BOT_PREFIX + "]\s?(ADD|Add|add)(_|\s|-)?(MODPACK|Modpack|modpack)", message) is not None:
            if info: print("INFO: 'add modpack' command received")
            await add_modpack(message, args)

        # Insults a specified user
        elif re.search("^["+BOT_PREFIX+"]\s?(INSULT|insult|Insult)", message) is not None:
            if info: print("INFO: 'insult' command received.")
            #TODO insult command

        # Seduces a specified user
        elif re.search("^["+BOT_PREFIX+"]\s?(SEDUCE|seduce|Seduce)", message) is not None:
            if info: print("INFO: 'seduce' command received.")
            #TODO seduce command

        # Threatens a specified user
        elif re.search("^["+BOT_PREFIX+"]\s?(THREATEN|Threaten|threaten)", message) is not None:
            if info: print("INFO: 'threaten' command received.")
            #TODO threaten command

        # Convert one currency to another
        elif re.search("^["+BOT_PREFIX+"]\s?(CONVERT|Convert|convert)", message) is not None:
            if info: print("INFO: 'convert' command received.")
            #TODO currency convert command

        # Command for setting age-related roles
        elif re.search("^["+BOT_PREFIX+"]\s?(IAM|I'm|iam|Iam|im|Im|i'm)", message) is not None:
            if info: print("INFO: 'iam' command received.")
            #TODO iam (age) command

        # Role for getting Depth shark teams (5 max)
        elif re.search("^["+BOT_PREFIX+"]\s?(TEAM|Team|team)(_|\s|-)(SHARKS|Sharks|sharks)", message) is not None:
            if info: print("INFO: 'team sharks' command received.")
            #TODO team sharks command

        # Role for splitting tagged people into teams
        elif re.search("^["+BOT_PREFIX+"]\s?(TEAM|TEAMS|team|teams)", message) is not None:
            if info: print("INFO: 'team' command received.")
            #TODO team command

        # Help command
        elif re.search("^["+BOT_PREFIX+"]\s?(HELP|help|Help)", message) is not None:
            if info: print("INFO: 'help' command received.")
            #TODO help command

        # SteamID command - returns steam IDs
        elif re.search("^["+BOT_PREFIX+"]\s?(Steam|steam|STEAM)(ID|id|Id)", message) is not None:
            if info: print("INFO: 'SteamID' command received.")
            #TODO steamID command

        # Stream Announcement command
        elif re.search("^["+BOT_PREFIX+"]\s?(STREAM|Stream|stream)(_|\s|-)?(ANNOUNCE|Announce|announce)", message) is not None:
            if info: print("INFO: 'StreamAnnounce' command received.")
            #TODO streamannounce command

        # Event Announcement command
        elif re.search("^["+BOT_PREFIX+"]\s?(EVENT|Event|event)(_|\s|-)?(ANNOUNCE|Announce|announce)", message) is not None:
            if info: print("INFO: 'EventAnnounce' command received.")
            #TODO eventannounce command

        # Gimme role command
        elif re.search("^["+BOT_PREFIX+"]\s?(GIMME|Gimme|gimme)|(Give me|GIVE ME|Give Me|give me)", message) is not None:
            if info: print("INFO: 'Gimme' command received.")
            #TODO gimme command

        # Alt name command
        elif re.search("^[" + BOT_PREFIX + "]\s?(ALT|Alt|alt)(_|\s|-)?(NAME|Name|name)", message) is not None:
            if info: print("INFO: 'Alt Name' command received.")
            #TODO Alt-Name command

        # Update command
        elif re.search("^["+BOT_PREFIX+"]\s?(UPDATE|Update|update)", message) is not None:
            if info: print("INFO: 'Update' command received.")
            #TODO update command

    # Update user's XP based on message
    xpUser(10, author)


# ---[ Bot Commands ]---
# Bot Help Command
async def help(message, args):
    if len(args) > 0:
        # Check which command was entered for help

    else:
        await message.channel.send("}status - Shows the status of the bot\n}roll x y - Roles x amount of y "
                           "sided dice\n}flip - Flips a coin\n}teams x @user @user... - Creates x "
                           "randomised teams containing any amount of users\n}teams_sharks @user "
                           "@user - shark selection for depth\n}insult @user - insults a user"
                           "\n}threaten @ user - threatens a user\n}seduce @user - seduces a user"
                           "\n}convert USD GBP amount - converts an amount from one currency to another"
                           "\n}streamannounce (role) (minutes to delete in) (game you are streaming) "
                           "(stream link)"
                           "\n}eventannounce (role) (minutes to delete in) (how many minutes till event start) "
                           "(game name) (server ip - optional)"
                           "\nThe roles for stream & event announce are: **M** - Members, **E** - Members + Temp Members"
                           ", **W** - Weebs, **S** - Streamers, **A** - Artists, **N** - Won't mention anyone!"
                           "\nNote: You can only mention one of these per announcement - so choose wisely"
                           "\n}Gimme - gives you roles such as 'artists' (Not Membership roles!)"
                           "\nUsage example: }Gimme artists")

# Dice Roll Command
async def roll_dice(message, args):
    tosend = ""

    if len(args) > 2 or len(args) < 2:
        if warnings: print("WARNING: 'roll' command called without correct number of args.")
        await message.channel.send("**Error:** }roll should be used with two numbers.")
        return

    try:
        # Send values specified in message to int
        no_dice = int(args[1])
        no_sides = int(args[2])

        # Check size - avoid excess calculation
        if no_dice > 10:
            no_dice = 10
        if no_sides > 100:
            no_sides = 100

        # Run dice-rolls
        for die in range(no_dice):
            roll = random.randint(1, no_sides)
            tosend += "{0}, ".format(roll)

        # Send Message
        await message.channel.send(tosend)
        return

    except ValueError:
        if warnings: print("WARNING: 'roll' command called with non-numeric args.")
        await message.channel.send("**Error:** }roll should be used with two numbers.")
        return


# Coin Flip Command
async def flip_coin(message):
    tosend = ""

    # Run coin-flip
    flip = bool(random.getrandbits(1))
    if flip:
        tosend += "Heads!"
    else:
        tosend += "Tails!"

    await message.channel.send(tosend)


# Get-Modpacks Command
async def get_modpacks(message):
    # Grab list of modpacks associated with this server
    modpack_list = dbGet("SELECT packName, game, packLink FROM modpacks WHERE guildID = {0};".format(message.guild.id))
    tosend = ""
    for pack in modpack_list:
        tosend += "**{0}:** ({1}) {2}\n".format(pack[0], pack[1], pack[2])
    message.channel.send(tosend)


# Add-Modpack Command
async def add_modpack(message, args):
    dbSet("INSERT INTO modpacks (packName, game, guildID, packLink) VALUES {0}, {1}, {2}, {3}".format(args[0], args[1], message.guild.id, args[2]))
    message.channel.send("Modpack collection updated with: *{0}*".format(args[0]))


# Insult Command
async def insult(message, args):
    # insults list
    insults = [" Your father was a hamster, and your mother smelled like elderberries!", " knows nothing!",
               " looks like Akif", " needs to construct additional Pylons",
               " is a big smelly willy", " is no real super sand lesbian!", " thinks ketchup is spicy",
               " votes for trump", " thinks the Moon is real", " believes the world is ROUND! LOL"
               " is almost as mediocre at Overwatch as Akif", " lets face it, you're past your best at this point.",
               " is a troglodyte"]

    for i in range(len(args)):
        if "@" not in args[i]:
            if warnings: print("WARNING: 'insult' command was called without a tagged user argument.")
        tosend = ""
        tosend += args[i]
        tosend += insults[random.randint(0, len(insults) - 1)]
        await message.channel.send(tosend)


# ---[ Start Bot ]---
# Check for Database
if not os.path.isfile('bot2.db'):
    if warnings: print("WARNING: bot2.db was not found. Rebuilding...")
    dbBuild()
    if warnings: print("bot2.db has been rebuilt.")
dbUpdate()

if not info: print("INFO: disabled")
if not warnings: print("WARNINGS: disabled")

client.run(TOKEN)
