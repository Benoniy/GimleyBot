'''
BasicBot
Code lifted from StockImage bot by meed223 with other minor contributors
All code has been severely simplified to provide a basic skeleton of a discord bot
'''

# ---[ Imports ]---
import time
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

# This switcher is based on the names of commands
class Switcher(object):
    def indirect(self, i, message, args):
        method = getattr(self, i, lambda: "invalid")
        return method(message, args)

    def help(self, message, args):
        return bot_help(message)

    def status(self, message, args):
        return message.channel.send("Dominatrix Bot 2.0 is Online.")

    def roll(self, message, args):
        return roll_dice(message, args)

    def flip(self, message, args):
        return flip_coin(message)

    def teams(self, message, args):
        return team_gen(message, args)

    def ip(self, message, args):
        return getIP(message)

    def announce(self, message, args):
        return announce(message, args)


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
    o_args = message.content.split(' ')


    # Message recieved - bot should only reply to users, not other bots
    if author != client.user and BOT_PREFIX in message.content:
        # Remove prefix
        o_args[0] = o_args[0].replace(BOT_PREFIX, "")

        # Remove blank spaces
        args = []
        for arg in o_args:
            if regex.search("[A-Z]+|[a-z]+|\d+", arg):
                args.append(arg)

        # Extract command from args
        command = args[0].lower()
        del args[0]
        switch = Switcher()
        await switch.indirect(command, message, args)

        '''
        # IP-Get Command
        elif regex.search("^[" + BOT_PREFIX + "]\s?(IP|Ip|ip)(\s|-|_)?(ADDRESS|Address|address)?",
                          message.content) is not None:
            await getIP(message)
        '''


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
    # TODO confirm this displays outside IP and not internal (This doesnt work)
    await message.channel.send("**Hostname:** {0}\n**IP:** {1}".format(
        socket.gethostname(),
        socket.gethostbyname(socket.gethostname())
    ))


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
