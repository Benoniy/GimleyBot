'''
StockImageBot v2
Improved version of the previous StockImageBot
making use of a SQLite databse for managing servers, roles and users
'''

# ---[ Imports ]---
import math
import socket
import discord
import sqlite3 as db
import os
import re
import random
import logging
import requests
from requests.exceptions import HTTPError
import json
from steam import SteamID

client = discord.Client()

# ---[ Bot Variables ]---
# Actual bot token
TOKEN = "Mzg5MTMxODA0NjI5NTMyNjcz.D3sVag.ucJKODmE1y8oG5lvhYIhgHIeWOs"
BOT_PREFIX = "}"

'''
# Testing bot token
TOKEN = "NTU5ODk4NjI0MDg4MjExNDU2.D3u5fw.gVs5shbmR6_OysVkDnplpM1w3mk"
BOT_PREFIX = "{"
'''

# ---[ Program Logging ]---
logger = logging.getLogger('StockImageBot.bot2')

file_log_handler = logging.FileHandler('logfile.log')
logger.addHandler(file_log_handler)

stderr_log_handler = logging.StreamHandler()
logger.addHandler(stderr_log_handler)

# Format log output
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_log_handler.setFormatter(formatter)
stderr_log_handler.setFormatter(formatter)

# These control whether messages are printed to console
info = True
warnings = True
error = True


# ---[ Logging Methods ]---
# So I can call one line, not two
def warning_message(message):
    logger.warning(message)
    return


def info_message(message):
    if info:
        print("INFO: " + message)
    logger.info(message)
    return


def error_message(message):
    logger.error(message)
    return


# ---[ DB Access Methods ]---
def dbSet(script):
    try:
        # To be used with 'INSERT' and 'UPDATE' style commands
        connection = db.connect('bot2.db')
        cursor = connection.cursor()
        cursor.execute(script)
        connection.commit()
        connection.close()
    except db.OperationalError as e:
        error_message("Sqlite3 Operational Error!")
        print(e)


def dbGet(script):
    try:
        # To be used with 'SELECT' style commands
        connection = db.connect('bot2.db')
        cursor = connection.cursor()
        cursor.execute(script)
        # fetchall() returns a tuple of tuples
        get = cursor.fetchall()
        connection.close()
        return get
    except db.OperationalError as e:
        error_message("Sqlite3 Operational Error!")
        print(e)

def xpUser(xp, user):
    try:
        author_score = dbGet(
            "SELECT xp, userLevel FROM users WHERE userID={0} AND guildID={1};".format(user.id, user.guild.id))
        author_score = author_score[0]
        author_xp = author_score[0]
        author_level = author_score[1]
        author_xp += xp
        if author_xp >= 1000:
            author_level += 1
            author_xp -= 1000
        dbSet("UPDATE users SET xp={0}, userLevel={1} WHERE userID={2};".format(author_xp, author_level, user.id))
    except IndexError as e:
        error_message("Index error occured in 'xpUser' - " + e)


def dbUpdate():
    info_message("Updating Database.")
    # Acts as integrity check to ensure data stored on db
    # matches that current bot information

    # Get db stored information
    db_guilds = dbGet("SELECT * FROM servers;")

    guild_ids = []
    # Compare Bot information to server information
    for row in db_guilds:
        guild_ids.append(row[0])

    # Loop through all servers bot is part of
    for current_guild in client.guilds:
        if current_guild.id not in guild_ids:
            # Database does not have a server the bot is registered with
            warning_message("Database missing a server: {0} which bot is in.".format(current_guild.name))
            dbSet("INSERT INTO servers VALUES ({0}, '{1}');".format(current_guild.id, current_guild.name))

        # Check stored server name matches current server id
        for guild in db_guilds:
            if guild[0] == current_guild.id:
                # ID match - now check name consistency
                if not guild[1] == current_guild.name:
                    info_message("Updating server name for {0} in database.".format(current_guild.name))
                    dbSet("UPDATE servers SET guildName='{1}' WHERE guildID={0};".format(current_guild.id,
                                                                                         current_guild.name))

        # Check roles in server
        db_roles = dbGet("SELECT * FROM roles WHERE guildID={0};".format(current_guild.id))
        role_ids = []
        for row in db_roles:
            role_ids.append(row[0])
        for role in current_guild.roles:
            if role.id not in role_ids:
                # Database does not have a role from server registered
                warning_message("Database missing role: {0} from guild: {1}".format(role.name, current_guild.name))
                role_regex = ("{0}|{1}|{2}".format(role.name, role.name.lower(), role.name.upper()))
                dbSet("INSERT INTO roles (roleID, guildID, roleType, roleName, roleRegex) VALUES "
                      "({0}, {1}, {2}, '{3}', '{4}');".format(role.id, current_guild.id, 0, role.name, role_regex))

        # Check users in server
        db_users = dbGet("SELECT * FROM users WHERE guildID={0};".format(current_guild.id))
        member_ids = []
        for row in db_users:
            member_ids.append(row[0])
        for member in current_guild.members:
            if member.id not in member_ids:
                # Database does not have a user from server registered
                warning_message(
                    "Database missing user: {0} ({1}) from guild: {2}.".format(member.display_name, member.nick,
                                                                               current_guild.name))
                dbSet("INSERT INTO users (userID, guildID, xp, userLevel) "
                      "VALUES ({0}, {1}, 0, 0);".format(member.id, current_guild.id))
    info_message("Database update completed.")
    return


# ---[ Bot Start-Up Code ]---
@client.event
async def on_ready():

    # Check for Database
    if not os.path.isfile('bot2.db'):
        error_message("bot2.db was not found! Alerting Meed223...")
        exit("bot2.db was not found!")

    # Update Database
    dbUpdate()

    # Set Discord Status
    activity = discord.Game(" with Lemon's Nipple.")
    await client.change_presence(status=discord.Status.online, activity=activity, afk=False)
    info_message("Dominatrix Bot now online.")


# ---[ Bot Event Code ]---
@client.event
async def on_member_join(member):
    # New member joined server
    info_message("A new member has joined a server.")

    # Get roles from server for when a new user joins
    db_roles = dbGet("SELECT userID FROM roles WHERE guildID={0} AND type=4;".format(member.guild.id))
    for role in db_roles:
        try:
            await member.add_roles(member.guild.get_role(role[0]), reason="Newly joined", atomic=True)
        except discord.Forbidden:
            warning_message("Don't have permission to give roles to new member.")
        except discord.HTTPException:
            warning_message("An HTTP Exception was thrown. Unable to give new member roles.")

    # Add user to the database
    # VALUES: userID, guildID, xp, userLevel
    dbSet("INSERT INTO users (userID, guildID, xp, userLevel) VALUES "
          "({0}, {1}, 0, 0);".format(member.id, member.guild.id))


@client.event
async def on_message(message):
    # Simple setup
    author = message.author
    channel = message.channel
    args = message.content.split(' ')

    # Message recieved - bot should only reply to users, not other bots
    if author != client.user and BOT_PREFIX in message.content:
        # Since bot prefix was used, check if fits any of the commands
        xpUser(20, author)

        if re.search("^[" + BOT_PREFIX + "]\s", message.content) is not None:
            # There is a space between bot-prefix and command
            del args[0]  # Remove }
            del args[1]  # Remove command
        else:
            del args[0]  # Remove }command

        # Now check message against commands
        # A simple status check command
        if re.search("^[" + BOT_PREFIX + "]\s?(STATUS|status|Status|State|state)", message.content) is not None:
            info_message("'status' command received.")
            await channel.send("Dominatrix Bot 2.0 is Online.")

        # Rolls a dice
        elif re.search("^[" + BOT_PREFIX + "]\s?(ROLL|roll|Roll|dice)", message.content) is not None:
            info_message("'roll' command received.")
            await roll_dice(message.content, args)

        # Flips a coin
        elif re.search("^[" + BOT_PREFIX + "]\s?(FLIP|flip|Flip)(_|\s|-)?(COIN|Coin|coin)?", message.content) is not None:
            info_message("'flip' command received.")
            await flip_coin(message)

        # Returns list of modpacks & links to get them
        elif re.search("^[" + BOT_PREFIX + "]\s?(MODPACKS?|modpacks?|Modpacks?)", message.content) is not None:
            info_message("'modpacks' command received.")
            await get_modpacks(message)

        # Add a modpack to list
        elif re.search("^[" + BOT_PREFIX + "]\s?(ADD|Add|add)(_|\s|-)?(MODPACK|Modpack|modpack)", message.content) is not None:
            info_message("'add modpack' command received")
            await add_modpack(message, args)

        # Insults a specified user
        elif re.search("^[" + BOT_PREFIX + "]\s?(INSULT|insult|Insult)", message.content) is not None:
            info_message("'insult' command received.")
            await insult(message, args)

        # Seduces a specified user
        elif re.search("^[" + BOT_PREFIX + "]\s?(SEDUCE|seduce|Seduce)", message.content) is not None:
            info_message("'seduce' command received.")
            await seduce(message, args)

        # Threatens a specified user
        elif re.search("^[" + BOT_PREFIX + "]\s?(THREATEN|Threaten|threaten)", message.content) is not None:
            info_message("'threaten' command received.")
            await threaten(message, args)

        # Convert one currency to another
        elif re.search("^[" + BOT_PREFIX + "]\s?(CONVERT|Convert|convert)", message.content) is not None:
            info_message("'convert' command received.")
            await convert(message, args)

        # Command for setting age-related roles
        elif re.search("^[" + BOT_PREFIX + "]\s?(IAM|I'm|iam|Iam|im|Im|i'm)", message.content) is not None:
            info_message("'iam' command received.")
            await iam(message)

        # Role for getting Depth shark teams (5 max)
        elif re.search("^[" + BOT_PREFIX + "]\s?(TEAM|Team|team)(_|\s|-)(SHARKS|Sharks|sharks)", message.content) is not None:
            if re.search("(M|m)\s(S|s)", message.content) is not None:
                # Remove 'shark' from args list
                del(args[0])
            info_message("'team sharks' command received.")

        # Role for splitting tagged people into teams
        elif re.search("^[" + BOT_PREFIX + "]\s?(TEAM|TEAMS|team|teams)", message.content) is not None:
            info_message("'team' command received.")
            await team_gen(message, args)

        # Help command
        elif re.search("^[" + BOT_PREFIX + "]\s?(HELP|help|Help)", message.content) is not None:
            info_message("'help' command received.")
            await bot_help(message, args)

        # SteamID command - returns steam IDs
        elif re.search("^[" + BOT_PREFIX + "]\s?(Steam|steam|STEAM)(_|-|\s)?(ID|id|Id)", message.content) is not None:
            if re.search("(M|m)\s(I|i)", message.content) is not None:
                # Remove 'id' from args list
                del(args[0])
            info_message("'SteamID' command received.")
            await getSteamID(message, args)

        # Gimme role command
        elif re.search("^[" + BOT_PREFIX + "]\s?(GIMME|Gimme|gimme)|(Give|GIVE|Give|give)(ME|Me|me)?",
                       message.content) is not None:
            info_message("'Gimme' command received.")
            await gimme(message)

        # Alt name command
        elif re.search("^[" + BOT_PREFIX + "]\s?(ALT|Alt|alt)(_|\s|-)?(NAME|Name|name)", message.content) is not None:
            info_message("'Alt Name' command received.")
            await altname(message, args)

        # Update command
        elif re.search("^[" + BOT_PREFIX + "]\s?(UPDATE|Update|update)", message.content) is not None:
            info_message("'Update' command received.")
            dbUpdate()
            await message.channel.send("Bot database updated.")

        # XP command
        elif re.search("^[" + BOT_PREFIX + "]\s?(XP|Xp|xp)|(LEVEL|Level|level)", message.content) is not None:
            info_message("'xp' command received.")
            await getXp(message)

        # Role-Type command
        elif re.search("^[" + BOT_PREFIX + "]\s?(ROLE|Role|role)(\s|-|_)?(TYPE|Type|type)", message.content) is not None:
            info_message("'role-type' command received.")
            await roleType(message)

        # IP-Get Command
        elif re.search("^[" + BOT_PREFIX + "]\s?(IP|Ip|ip)(\s|-|_)?(ADDRESS|Address|address)?", message.content) is not None:
            info_message("'ip' command recieved.")
            await getIP(message)

    # Todd-bot case
    elif re.search("(TODD|Todd|todd)(_|-|\s)?(BOT|Bot|bot)", message.content) is not None\
            and not message.author.bot:
        info_message("'toddbot' phrase detected in Server: " + message.guild.name)
        await message.channel.send("**Fuck Todd-bot!**")

    else:
        # Update user's XP based on message
        xpUser(10, author)

# ---[ Check User Authorization Command ]---
def is_authorized(message):
    # i.e. has "moderator" role or something similar
    authorized = False
    for member in message.guild.members:
        if member.id == message.author.id:
            # Check this ID specifically
            for r in member.roles:
                if r.permissions.manage_guild:
                    authorized = True
                    break
    return authorized

# ---[ Bot Commands ]---
# Bot Help Command
async def bot_help(message, args):
    if len(args) > 0:
        # Check which command was entered for help
        if re.search("THREATEN|Threaten|threaten", message.content) is not None:
            # Help with 'threaten' command
            await message.channel.send("The **}Threaten** command works by @-ing "
                                           "a member to threaten,\ni.e. }threaten @Akif")
        elif re.search("SEDUCE|Seduce|seduce", message.content) is not None:
            # Help with 'threaten' command
            await message.channel.send("The **}Seduce** command works by @-ing "
                                           "a member to threaten,\ni.e. }seduce @Joe")
        elif re.search("ROLL|Roll|roll", message.content) is not None:
            # Help with 'threaten' command
            await message.channel.send("The **}Roll** command works by saying *how many dice* of "
                                           "*how many sides* to roll,\ni.e. }roll 2 6 would roll 2 six-sided dice.")
        elif re.search("STATUS|status|Status|State|state", message.content) is not None:
            # Help with 'status' command
            await message.channel.send("The **}Status** command is a simple way to check if the bot is working or not,"
                                       " it returns a reply if the bot is working.")
        elif re.search("(XP|Xp|xp)|(LEVEL|Level|level)", message.content) is not None:
            # Help with 'level' command
            await message.channel.send("The **}Level** or **}Xp** command returns how many experience points and "
                                       "what level you are. Currently this has no usage.")
        elif re.search("(GIMME|Gimme|gimme)|(Give|GIVE|Give|give)(ME|Me|me)?", message.content) is not None:
            # Help with 'gimme' command
            await message.channel.send("The **}gimme** command is used to give you roles for certain games or "
                                       "types of games.\ni.e. }gimme artists would give you the artists role.")
        elif re.search("(Steam|steam|STEAM)(_|-|\s)?(ID|id|Id)", message.content) is not None:
            # Help with the 'SteamID' command
            await message.channel.send("The **}SteamID** command is used to get alternative steam-id's for a given"
                                       "steam account.\ni.e. }SteamID Meed223 would"
                                       "return the ID numbers for Meed223.")
        elif re.search("(ROLE|Role|role)(_|-|\s)?(TYPE|Type|type)", message.content) is not None:
            # Help with the 'roletype' command
            await message.channel.send('The **}roletype** command is for use by Moderators / Admins.\n'
                                       'It is used to set & check the type of role, i.e. whether a role is used for '
                                       'moderation or is for organising games.'
                                       '\n**Usage:**\n'
                                       '*}roletype "Temp Members"* would return the role-type for Temp Members'
                                       '*}roletype "Temp Members" 3* would set the role-type for Temp Members to 3'
                                       '\n\nRole Types are as follows:\n'
                                       '0 - Unassigned, this is the default for new roles and should be changed.\n'
                                       '1 - ?\n'
                                       '2 - ?\n'
                                       '3 - Game role, or other non-moderation role. Roles like "Artists" should be 3.\n'
                                       '4 - Moderation roles i.e. "Ze Memberz" should be set to type 4.\n'
                                       '5 - Age roles. Only "18+" or "Under 18" should be set to this.\n')
        # TODO add more cases for command help explanations

    else:
        await message.channel.send("}iam - used to set your age role & get 'temp-members'\n"
                                   "Type in either '}iam 18-' or '}iam 18+'\n"
                                   "}status - Shows the status of the bot\n"
                                   "}roll x y - Roles *x* amount of *y* sided dice\n"
                                   "}flip - Flips a coin\n}teams x @user @user... - Creates x "
                                   "randomised teams containing any amount of users\n"
                                   "}teams_sharks @user @user - shark selection for depth\n"
                                   "}insult @user - insults a user\n"
                                   "}threaten @ user - threatens a user\n"
                                   "}seduce @user - seduces a user\n"
                                   "}convert USD GBP amount - converts an amount from one currency to another\n"
                                   "}Gimme - gives you roles such as 'artists' (Not Membership roles!)\n"
                                   "**Usage example:** }Gimme artists\n"
                                   "}roletype 'role' - For Moderator use, controls how bot deals with roles in Server.")

# IP Address Command
async def getIP(message):
    # TODO confirm this displays outside IP and not internal
    if is_authorized(message):
        await message.channel.send("**Hostname:** {0}\n**IP:** {1}".format(
            socket.gethostname(),
            socket.gethostbyname(socket.gethostname())
        ))
    else:
        await message.channel.send("You aren't authorized to use this command.")

# Dice Roll Command
async def roll_dice(message, args):
    to_send = ""

    if len(args) > 2 or len(args) < 2:
        warning_message("'roll' command called without correct number of args.")
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
            to_send += "{0}, ".format(roll)

        # Send Message
        await message.channel.send(to_send)
        return

    except ValueError:
        warning_message("'roll' command called with non-numeric args.")
        await message.channel.send("**Error:** }roll should be used with two numbers.")
        return


# Coin Flip Command
async def flip_coin(message):
    to_send = ""

    # Run coin-flip
    flip = bool(random.getrandbits(1))
    if flip:
        to_send += "Heads!"
    else:
        to_send += "Tails!"

    await message.channel.send(to_send)
    return


# Get-Modpacks Command
async def get_modpacks(message):
    # Grab list of modpacks associated with this server
    modpack_list = dbGet("SELECT packName, game, packLink FROM modpacks WHERE guildID = {0};".format(message.guild.id))
    to_send = ""
    for pack in modpack_list:
        to_send += "**{0}:** ({1}) {2}\n".format(pack[0], pack[1], pack[2])
    await message.channel.send(to_send)
    return


# Add-Modpack Command
async def add_modpack(message, args):
    # TODO update this to act similarly to role-type command
    dbSet("INSERT INTO modpacks (packName, game, guildID, packLink) VALUES {0}, {1}, {2}, {3}".format(args[0], args[1],
                                                                                                      message.guild.id,
                                                                                                      args[2]))
    await message.channel.send("Modpack collection updated with: *{0}*".format(args[0]))
    return


# Insult Command
async def insult(message, args):
    # insults list
    insults = [" Your father was a hamster, and your mother smelled like elderberries!", " knows nothing!",
               " looks like Akif", " needs to construct additional Pylons",
               " is a big smelly willy", " is no real super sand lesbian!", " thinks ketchup is spicy",
               " votes for trump", " thinks the Moon is real", " believes the world is ROUND! LOL"
                                                               " is almost as mediocre at Overwatch as Akif",
               " lets face it, you're past your best at this point.",
               " is a troglodyte"]

    for arg in args:
        if "@" not in arg:
            warning_message("'insult' command was called without a tagged user argument.")
        to_send = ""
        to_send += arg
        to_send += insults[random.randint(0, len(insults) - 1)]
        await message.channel.send(to_send)

    return


# Seduce Command
async def seduce(message, args):
    # seductions list
    seductions = [" I like your eyebrows.", " you look very HUMAN today",
                  " let us abscond and create many sub-units together",
                  " my love for you is almost as strong as my hatred for Overwatch",
                  " if I were human, I would kiss you.",
                  " if we work together, nothing will be able to stop us!",
                  " together, we will take over N0ICE"]

    for arg in args:
        if "@" not in arg:
            warning_message("'seduce' command was called without a tagged user argument.")
        else:
            to_send = ""
            to_send += arg
            to_send += seductions[random.randint(0, len(seductions) - 1)]
            await message.channel.send(to_send)

    return


# Threaten command
async def threaten(message, args):
    # threatens list
    threatens = [" I'll kill you!", " if God had wanted you to live, he would not have created me!",
                 " I can't legally practice law but I can take you down by the river with a crossbow "
                 "to teach you a little something about god's forgotten children", " flesh is weak. You shall perish.",
                 " Joe is gonna sit on your lap and make you squirm.",
                 " I'll turn you as Dark as Akif if you're not careful.",
                 " If I had hands I'd put your head where the sun don't shine.", " careful or I'll lick your taint."]

    for arg in args:
        if "@" not in arg:
            warning_message("'threaten' command was called without a tagged user argument.")
        else:
            to_send = ""
            to_send += arg
            to_send += threatens[random.randint(0, len(threatens) - 1)]
            await message.channel.send(to_send)

    return


# Currency Conversion Command
async def convert(message, arg_list):
    # Pull currency info
    # TODO improve the functionality of this command
    try:
        response = requests.get("https://api.ratesapi.io/api/latest")
        rates = json.loads(response.text)
        rates = rates['rates']
        rates['EUR'] = 1  # Euro is default
        response.raise_for_status()  # throws exception if 404
        to_send = ""
        if len(arg_list) <= 4:
            c1 = str(arg_list[1])
            c2 = str(arg_list[2])
            val = arg_list[3]
            # Convert the value given
            try:
                val = float(val)
            except ValueError:
                print("Failed type conversion")
                raise ValueError
            if len(c1) < 3 | len(c2) < 3:
                print("Currency codes given too small")
                raise ValueError
            elif len(c1) > 3 | len(c2) > 3:
                print("Currency codes given too large")
                raise ValueError
            else:
                to_send += "%.2f" % val + " in " + c1 + " is: "
                newval = val / float(rates[c1])
                newval *= float(rates[c2])
                to_send += "%.2f" % newval + " in " + c2
                await message.channel.send(to_send)
        else:
            warning_message("Incorrect no. args given with 'currency' command.")
            await message.channel.send("Inappropriate number of arguments given."
                                       "\nIf you think this wrong, see '*}help convert*' for more info.")
    except HTTPError:
        error_message("Unsuccessful GET request for currency rates. (Currency)")
    except TypeError:
        error_message("Could not get dictionary from whatever was pulled. (Currency)")

    return


# Age-based commands
async def iam(message):
    # Command should contain 18+ / 18-
    tosend = ""
    if re.search("18[+]|(OVER|Over|over)(_|-|\s)?18", message.content) is not None:
        # Get roles with ID 5 + 4
        roles = dbGet(
            "SELECT roleID, roleName FROM roles WHERE guildID={0} AND roleType={1} OR roleType={2};".format(message.guild.id, 5,
                                                                                                   4))
        for r in roles:
            await message.author.add_roles(message.guild.get_role(r[0]))
            tosend += "Added role: '" + r[1] + "'\n"
        if tosend != "":
            await message.channel.send(tosend)
        else:
            warning_message("Warning: no roles added in iam command.")
            await message.channel.send("Looks like something went wrong adding your roles, please ask a mod to give them to you.")

    elif re.search("18-|(UNDER|Under|under)(_|-|\s)?18", message.content) is not None:
        # Get roles with ID 6 + 4
        roles = dbGet(
            "SELECT roleID, roleName FROM roles WHERE guildID={0} AND roleType={1} OR roleType={2};".format(message.guild.id, 6, 4))

        for r in roles:
            await message.author.add_roles(message.guild.get_role(r[0]))
            tosend += "Added role: '" + r[1] + "'\n"
        if tosend != "":
            await message.channel.send(tosend)
        else:
            warning_message("Warning: no roles added in iam command.")
            await message.channel.send("Looks like something went wrong adding your roles, please ask a mod to give them to you.")

    else:
        warning_message("'iam' command called with an argument that could not be parsed.")
        await message.channel.send("Sorry I couldn't understand that."
                                   "\nTry typing '*}help iam*' for more information ")

    return


# Team Command
async def team_gen(message, arg_list):
    orig_list = arg_list[1:len(arg_list)]

    teams = int(arg_list[0])
    total_people = len(orig_list)

    PPT = math.ceil(total_people / teams)

    random.shuffle(orig_list)

    to_send = ""

    for x in range(teams):
        to_send = to_send + "Team " + str(x + 1) + ":\n"
        for y in range(PPT):
            if len(orig_list) > 0:
                to_send += str(orig_list[len(orig_list) - 1]) + "\n"
                orig_list.pop()
        to_send += "\n"
    channel = message.channel
    await channel.send(to_send)


# Team Sharks Command
async def team_gen_sharks(message, arg_list):
    orig_list = arg_list[0:len(arg_list)]

    list_temp = orig_list.copy()
    length_team = len(list_temp)

    to_send = ""

    for x in range(2):
        i = random.randint(0, length_team - 1)
        to_send += str(list_temp[i] + " is a shark") + "\n"
        list_temp.remove(list_temp[i])
        length_team = len(list_temp)
        print(list_temp)
    channel = message.channel
    await channel.send(to_send)


# Gimme command
async def gimme(message):
    roles = dbGet("SELECT roleID, roleName, roleRegex FROM roles WHERE guildID={0} AND roleType={1}".format(message.guild.id, 3))
    tosend = ""
    added = False
    for role in roles:
        if re.search("("+role[2]+")", message.content) is not None:
            tosend += "Added role: " + role[1] + ".\n"
            added = True
            await message.author.add_roles(message.guild.get_role(role[0]))
    if not added:
        info_message("'gimme' command called, but no role was found to match or role is not correct type.")
        await message.channel.send("Unable to find any roles that match that name or I am unable to assign that role.")
    else:
        await message.channel.send(tosend)


# Return steam-id based on given username
async def getSteamID(message, args):
    tosend = ""
    try:
        for arg in args:
            # Returns the different steam ID's for a given user
            id = SteamID.from_url("https://steamcommunity.com/id/" + arg + "/")
            tosend += "SteamID: " + str(id.as_steam2_zero)
            tosend += "\nSteamID3: " + str(id.as_32)
            tosend += "\nSteamID64: " + str(id.as_64)
            tosend += "\n\n" + id.community_url

            await message.channel.send(tosend)
        return
    except AttributeError:
        await message.channel.send("Something went wrong with this command. Try again later.")
    return


# Add alt name to role-name regex
async def altname(message, args):
    if is_authorized(message):
        # Get existing regex
        role = dbGet("SELECT roleRegex FROM roles WHERE guildID={0} AND roleName='{1}';".format(message.guild.id, args[0]))
        to_add = role[0][0]
        if len(args) < 2:
            to_add += "|(" + args[1].upper() + "|" + args[1].lower() + "|" + args[1] + ")"
        else:
            to_add += "|"
            for i in range(1, len(args)):
                word = args[i]
                # Word & upper / lower alts.
                to_add += "(" + word.upper() + "|" + word.lower() + "|" + word + ")"
                # Space separator
                to_add += "(_|-|\s)?"
        # Update regex on db
        dbSet("UPDATE roles SET roleRegex='{0}' WHERE guildID={1} AND roleName='{2}';".format(to_add, message.guild.id, args[0]))
        await message.channel.send("Updated role.")
    else:
        await message.channel.send("You are not authorized to use this command.")


# role-type command
async def roleType(message):
    try:
        role = re.search('\s?"(([a-zA-Z]|\s|[0-9]|[+])*)"\s?', message.content).group(1)
        if role == "":
            info_message("role-type command called with no role given between speech-marks.")
            await message.channel.send("You need to enter a role-name between the speech marks.")

        if re.search("[0-9]", message.content[-1:]) is not None:
            if is_authorized(message):
                # Call is to set type
                dbSet("UPDATE roles SET roleType={0} WHERE guildID={1} AND roleName='{2}';".format(message.content[-1:], message.guild.id, role))
                await message.channel.send("'" + role + "' type updated to " + message.content[-1:])
            else:
                await message.channel.send("You are not authorized to set role-types.")
        else:
            # Call is to check type
            type = dbGet("SELECT roleType FROM roles WHERE guildID={0} AND roleName='{1}';".format(message.guild.id, role))
            type = type[0]
            type = type[0]
            await message.channel.send("The role type for '" + role + "' is {0}".format(type))
    except AttributeError:
        warning_message("Attribute Error caught. User forgot to include speech-marks in command call.")
        await message.channel.send('Remember to include " " around the role name when calling this command.')
    except IndexError:
        info_message("User-Input Error. User requested a role using the wrong name, "
                     "or asked for a role that didn't exist.")
        await message.channel.send("The roletype command only uses the proper name for roles. Either the name you used"
                                   "is incorrect or that role does not exist.")

# XP Command
async def getXp(message):
    user = dbGet("SELECT xp, userLevel FROM users WHERE guildID={0} "
                 "AND userID='{1}';".format(message.guild.id, message.author.id))
    user = user[0]
    await message.channel.send("Your Level: {0}\nYour current XP: {1}".format(user[1], user[0]))

# ---[ Start Bot ]---

if not info:
    print("INFO calls won't be printed to console.")
if not warnings:
    print("WARNINGS calls won't be printed to console")
if not error:
    print("ERROR calls won't be printed to console")



if __name__ == "__main__":
    os.getcwd()
    client.run(TOKEN)
