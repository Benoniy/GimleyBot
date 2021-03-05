import discord
import socket
import random
import regex
import math
from bot import is_authorized


async def bot_help(message):
    """ Provides a list of commands to the user """
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


async def get_ip(message):
    # TODO confirm this displays outside IP and not internal (This doesnt work)
    await message.channel.send("**Hostname:** {0}\n**IP:** {1}".format(
        socket.gethostname(),
        socket.gethostbyname(socket.gethostname())
    ))


async def roll_dice(message, args):
    """ Rolls a specified number of user defined dice """
    to_send = ""

    if len(args) > 2 or len(args) < 2:
        await message.channel.send("**Error:** }roll should be used with two numbers.")
        pass

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

    except ValueError:
        await message.channel.send("**Error:** }roll should be used with two numbers.")


async def flip_coin(message):
    """ Flips a coin and displays the result """
    to_send = ""
    flip = bool(random.getrandbits(1))

    if flip:
        to_send += "Heads!"
    else:
        to_send += "Tails!"

    await message.channel.send(to_send)


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
