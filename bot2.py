'''
BasicBot
Code lifted from StockImage bot by meed223 with other minor contributors
All code has been severely simplified to provide a basic skeleton of a discord bot
'''

# ---[ Imports ]---
import math
import socket
import discord
import regex
import random
client = discord.Client()

# ---[ Bot Variables ]---
# Globals
TOKEN = ""
BOT_PREFIX = ""


def read_token():
    # Get token & prefix from file
    file = open("token.txt", "r")
    global TOKEN
    TOKEN = file.readline()
    TOKEN = TOKEN.replace("\n", "")
    print(TOKEN)
    global BOT_PREFIX
    BOT_PREFIX = file.readline()
    BOT_PREFIX = BOT_PREFIX.replace("\n", "")
    print(BOT_PREFIX)
    return [TOKEN, BOT_PREFIX]

# These control whether messages are printed to console
info = True

# ---[ Bot Start-Up Code ]---
@client.event
async def on_ready():
    # Set Discord Status
    activity = discord.Game("Testing bot")
    await client.change_presence(status=discord.Status.online, activity=activity, afk=False)


# ---[ Bot Event Code ]---
@client.event
async def on_member_join(member):
    # New member joined server
    print("member joined")


@client.event
async def on_guild_join(guild):
    # Joined a new server
    print("bot joined")

@client.event
async def on_message(message):
    # Simple setup
    author = message.author
    channel = message.channel
    args = message.content.split(' ')


    # Message recieved - bot should only reply to users, not other bots
    if author != client.user and BOT_PREFIX in message.content:
        print(args)
        # Since bot prefix was used, check if fits any of the commands
        if regex.search("^[" + BOT_PREFIX + "]\s", message.content) is not None:
            # There is a space between bot-prefix and command
            del args[0]  # Remove }
            del args[1]  # Remove command
        else:
            del args[0]  # Remove }command

        # Now check message against commands
        # A simple status check command

        if regex.search("^[" + BOT_PREFIX + "]\s?(STATUS|status|Status|State|state)", message.content) is not None:
            await channel.send("Dominatrix Bot 2.0 is Online.")

        # Rolls a dice
        elif regex.search("^[" + BOT_PREFIX + "]\s?(ROLL|roll|Roll|dice)", message.content) is not None:
            await roll_dice(message.content, args)

        # Flips a coin
        elif regex.search("^[" + BOT_PREFIX + "]\s?(FLIP|flip|Flip)(_|\s|-)?(COIN|Coin|coin)?",
                          message.content) is not None:
            await flip_coin(message)

        # Role for getting Depth shark teams (5 max)
        elif regex.search("^[" + BOT_PREFIX + "]\s?(TEAM|Team|team)(_|\s|-)(SHARKS|Sharks|sharks)",
                          message.content) is not None:
            if regex.search("(M|m)\s(S|s)", message.content) is not None:
                # Remove 'shark' from args list
                del (args[0])

        # Role for splitting tagged people into teams
        elif regex.search("^[" + BOT_PREFIX + "]\s?(TEAM|TEAMS|team|teams)", message.content) is not None:
            await team_gen(message, args)

        # Help command
        elif regex.search("^[" + BOT_PREFIX + "]\s?(HELP|help|Help)", message.content) is not None:
            await bot_help(message)

        # Alt name command
        elif regex.search("^[" + BOT_PREFIX + "]\s?(ALT|Alt|alt)(_|\s|-)?(NAME|Name|name)",
                          message.content) is not None:
            await altname(message, args)

        # Update command
        elif regex.search("^[" + BOT_PREFIX + "]\s?(UPDATE|Update|update)", message.content) is not None:
            await message.channel.send("Bot database updated.")

        # Role-Type command
        elif regex.search("^[" + BOT_PREFIX + "]\s?(ROLE|Role|role)(\s|-|_)?(TYPE|Type|type)",
                          message.content) is not None:
            await roleType(message)

        # IP-Get Command
        elif regex.search("^[" + BOT_PREFIX + "]\s?(IP|Ip|ip)(\s|-|_)?(ADDRESS|Address|address)?",
                          message.content) is not None:
            await getIP(message)

        # General-Announcement Command
        elif regex.search(
                "^[" + BOT_PREFIX + "]\s?(ANNOUNCE|Announce|announce)|(ANNOUNCEMENT|Announcement|announcement)",
                message.content) is not None:
            await announce(message, args)


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
async def bot_help(message):
    await message.channel.send("`}iam` - used to set your age role & get 'temp-members'\n"
                                "Type in either `}iam 18-` or `}iam 18+`\n"
                                "`}status` - Shows the status of the bot\n"
                                "`}roll x y` - Roles *x* amount of *y* sided dice\n"
                                "`}flip` - Flips a coin\n}teams x @user @user... - Creates x "
                                "randomised teams containing any amount of users\n"
                                "`}teams_sharks @user @user...` - shark selection for depth\n"
                                "`}insult @user` - insults a user\n"
                                "`}threaten @ user` - threatens a user\n"
                                "`}seduce @user` - seduces a user\n"
                                "`}convert USD GBP amount` - converts an amount from one currency to another. **Note:**"
                                "this command does not work currently.\n"
                                "`}Gimme` - gives you roles such as 'artists' (Not Membership roles!)\n"
                                "**Usage example:** `}Gimme artists`\n"
                                "`}roletype 'role'` - For Moderator use, controls how bot deals with roles in Server.")


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


# Add alt name to role-name regex
async def altname(message, args):
    try:
        if is_authorized(message):
            # get the full role name from between " " in message
            if not args[0][0] == '"':
                # Missing '"' at start
                await message.channel.send('You are missing " " around the role name you wish to '
                                           'update with an alt-name')
                return

            # loop through all args to find one that ends with a '"'
            found_end = False
            for i in range(0, len(args)):
                if args[i][-1:] == '"':
                    marker = i
                    found_end = True
                    # mark element that ends with '"'

            if not found_end:
                # no end '"' was found
                await message.channel.send('You are missing " " around the role name you wish to '
                                           'update with an alt-name')
                return

            # build role-name
            role_name = ""
            print("marker: {0}".format(marker))
            if marker != 0:
                for i in range(0, marker + 1):
                    role_name += args[i] + " "
                role_name = role_name[:-1:]  # Strip off whitespace at end of concatenated string
            else:
                role_name = args[marker]
            # remove '"' from start and end of string
            role_name = role_name[1::]
            role_name = role_name[:-1:]
            print(role_name)
        else:
            await message.channel.send("You are not authorized to use this command.")

    except IndexError:
        await message.channel.send(
            "Sorry, something went wrong. Try using the command again or try the help command to see if you used it correctly.")


# role-type command
async def roleType(message):
    try:
        role = regex.search('\s?"(([a-zA-Z]|\s|[0-9]|[+])*)"\s?', message.content).group(1)
        if role == "":
            await message.channel.send("You need to enter a role-name between the speech marks.")

        if regex.search("[0-9]", message.content[-1:]) is not None:
            if is_authorized(message):
                # Call is to set type
                await message.channel.send("'" + role + "' type updated to " + message.content[-1:])
            else:
                await message.channel.send("You are not authorized to set role-types.")
        else:
            # Call is to check type
            await message.channel.send("The role type for '" + role + "' is {0}")

    except AttributeError:
        await message.channel.send('Remember to include " " around the role name when calling this command.')

    except IndexError:
        await message.channel.send("The roletype command only uses the proper name for roles. Either the name you used"
                                   "is incorrect or that role does not exist.")


# announcement command
async def announce(message, args):
    announce_channel = discord.utils.get(message.guild.text_channels, name="general-tomfoolery")
    tosend = "**<@" + str(message.author.id) + "> would like to announce:**\n"
    try:
        for i in range(0, len(args)):
            tosend += args[i] + " "
        tosend += "\n*this message will automatically deleted in 30 minutes*"
        await message.channel.send("Message will be announced in #General-Tomfoolery and deleted 30 minutes from now.")
        to_delete = await announce_channel.fetch_message(announce_channel.last_message_id)
        await to_delete.delete(delay=1800)
    except IndexError:
        await message.channel.send("Please write a message. If you think you used this command correctly, "
                                   "consult the help command or ask Henry for help.")


# ---[ Start Bot ]---

if not info:
    print("INFO calls won't be printed to console.")

if __name__ == "__main__":
    # Assign values to globals
    print("a")
    read_token()

    # Run
    client.run(TOKEN)
