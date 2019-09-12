'''
Welcome to StockImageBot
A discord bot written in Python for StockImageSharks & N0ICE
'''

import discord
import random
import math

# ---[ Bot Setup ]---
'''
# Actual bot token
TOKEN = "Mzg5MTMxODA0NjI5NTMyNjcz.D3sVag.ucJKODmE1y8oG5lvhYIhgHIeWOs"
BOT_PREFIX = "}"
'''


# Testing bot token
TOKEN = "NTU5ODk4NjI0MDg4MjExNDU2.D3u5fw.gVs5shbmR6_OysVkDnplpM1w3mk"
BOT_PREFIX = "{"


client = discord.Client()


@client.event
async def on_ready():
    # sets status of bot to ready/online when code is run
    game = discord.Game("} help")
    await client.change_presence(status=discord.Status.idle, activity=game, afk=False)
    print("Dominatrix online\n")


@client.event
async def on_member_join(member):
    # Assigns 'noobies' role to a new member
    role = discord.utils.get(member.server.roles, name="Noobies")
    await member.add_roles(role, reason=None, atomic=True)
    print("New member has joined")


# Happens whenever a message
@client.event
async def on_message(message):

    # Bot should not reply to itself and use the prefix
    if message.author != client.user and BOT_PREFIX in message.content:
        message_content = message.content.upper()
        arg_list = message_content.split()
        print(message_content)
        channel = message.channel
        # Check what command was and call appropriate function
        if arg_list[0] == BOT_PREFIX + "STATUS":
            await channel.send("working")
            print("Printing status")

        # Roll dice
        elif arg_list[0] == BOT_PREFIX + "ROLL":
            try:
                await roll_dice(message, arg_list)
            except IndexError:
                await channel.send("Not enough arguments supplied, please see }help for instructions!")
                print("Error rolling dice, not enough args")
            except ValueError:
                await channel.send("Command can only accept numbers as arguments!")
                print("Error rolling dice, type error")

        # Flip a coin
        elif arg_list[0] == BOT_PREFIX + "FLIP":
            flip = random.randint(1, 3)
            if flip == 1:
                await channel.send("Heads")
                print("Heads")
            else:
                await channel.send("Tails")
                print("Tails")

        elif arg_list[0] == BOT_PREFIX + "INSULT":
            print("insult command recieved")
            try:
                await insult_gen(message, arg_list)
            except IndexError:
                await channel.send("You're the fool here! Try specifying someone to insult next time.")
                print("Error insulting, no user given to insult")
            except ValueError:
                print("Value Error in INSULT")

        elif arg_list[0] == BOT_PREFIX + "IAM":
            await role_assign(message, arg_list)

        elif arg_list[0] == BOT_PREFIX + "TEAMS":
            try:
                await team_gen(message, arg_list)
            except IndexError:
                await channel.send("Not enough arguments supplied, please see }help for instructions!")
                print("Error creating teams, not enough args")
            except ValueError:
                await channel.send("First argument can only be a number!")
                print("Error creating teams, type error")

        elif arg_list[0] == BOT_PREFIX + "TEAMS_SHARKS":
            try:
                await team_gen_sharks(message, arg_list)
            except IndexError:
                await channel.send("Not enough arguments supplied, please see }help for instructions!")
                print("Error creating teams, not enough args")
            except ValueError:
                await channel.send("First argument can only be a number!")
                print("Error creating teams, type error")

        elif arg_list[0] == BOT_PREFIX + "HELP":
            await send_help(message)

        # Admin commands
        elif BOT_PREFIX + "ADMIN" in arg_list[0]:
            if "ze moderators" in [y.name.lower() for y in message.author.roles]:
                if arg_list[0] == BOT_PREFIX + "ADMIN_HELP":
                    if "ze moderators" in [y.name.lower() for y in message.author.roles]:
                        await send_admin_help(message)

                elif arg_list[0] == BOT_PREFIX + "ADMIN_PURGE":

                        try:
                            await purge_amount(message, arg_list[1])
                        except IndexError:
                            await ("Not enough arguments supplied, please see }help for instructions!")
                            print("Error purging, not enough args")
                        except ValueError:
                            await channel.send("Argument can only be a number!")
                            print("Error purging, type error")


# ---[ Bot Commands ]---


async def team_gen(message, arg_list):
    orig_list = arg_list[2:len(arg_list)]

    teams = int(arg_list[1])
    total_people = len(orig_list)

    PPT = math.ceil(total_people / teams)

    random.shuffle(orig_list)

    to_send = ""

    for x in range(teams):
        to_send = to_send + "Team " + str(x+1) + ":\n"
        for y in range(PPT):
            if len(orig_list) > 0:
                to_send += str(orig_list[len(orig_list)-1]) + "\n"
                orig_list.pop()
        to_send += "\n"
    channel = message.channel
    await channel.send(to_send)


async def team_gen_sharks(message, arg_list):
    orig_list = arg_list[1:len(arg_list)]

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


# Prints out the bot help
async def send_help(message):
    channel = message.channel
    await channel.send("}status - Shows the status of the bot\n}roll x y - Roles x amount of y "
                                               "sized dice\n}flip - Flips a coin\n}teams x @user @user... - Creates x "
                                               "randomised teams containing any amount of users\n}teams_sharks @user "
                                               "@user - shark selection for depth")


# Prints out the admin bot help
async def send_admin_help(message):
    channel = message.channel
    await channel.send("}admin_purge x - deletes x amount of messages from the current chat and then the command")


# Roles x amount of y sized dice
async def roll_dice(message, arg_list):
    amount = int(arg_list[1])
    size = int(arg_list[2])
    print(amount)

    if amount > 10:
        amount = 10
    if size > 100:
        size = 100

    to_send = ""

    for x in range(amount):
        i = random.randint(1, size)
        to_send += str(i) + "\n"
    channel = message.channel
    await channel.send(to_send)


async def role_assign(message, arg_list):
    author = message.author
    # Only happens in server_guidelines
    if message.channel.name == "server_guidelines":
        temp_role = discord.utils.get(message.server.roles, name="Temp Members")

        # 18 or older
        if arg_list[1] == "18+":
            if "18-" in [y.name.lower() for y in message.author.roles]:
                role = discord.utils.get(message.server.roles, name="18-")
                await author.remove_roles(role)

            role = discord.utils.get(message.server.roles, name="18+")
            await author.add_roles(role)
            await author.send_message(message.channel, "Over 18")

        # Younger than 18
        elif arg_list[1] == "18-":
            if "18+" in [y.name.lower() for y in message.author.roles]:
                role = discord.utils.get(message.server.roles, name="18+")
                await author.remove_roles(role)
            role = discord.utils.get(message.server.roles, name="18-")
            await author.add_roles(role)
            await author.send_message(message.channel, "Under 18")

        # Remove noob role and add to temp members
        noob_role = discord.utils.get(message.server.roles, name="Noobies")
        await author.remove_roles(noob_role)
        await author.add_roles(temp_role)
        await purge_non_admin(message)


# Check if the message was sent by the bot
def is_me(m):
    return m.author == client.user


# Check if the message was sent by anyone with the Z moderators role
def is_admin(message):
    if "ze moderators" in [y.name.lower() for y in message.author.roles]:
        return False
    else:
        return True


# Check if the message was sent by anyone with the Z moderators role
async def purge_non_admin(message):
    if message.channel.name == "server_guidelines":
        channel = message.channel
        await channel.purge_from(message.channel, limit=100, check=is_admin)


async def purge_amount(message, limit):
    channel = message.channel
    await channel.purge_from(message.channel, limit=int(limit) + 1)


async def insult_gen(message, arg_list):
    #insults list
    insults = [" Your father was a hamster, and your mother smelled like elderberries!", " knows nothing!", " looks like Akif", " is a big smelly willy", " is no real super sand lesbian!", " thinks ketchup is spicy", " votes for trump", " is almost as mediocre at Overwatch as Akif", " lets face it, you're past your best at this point.", " is a troglodyte"]
    channel = message.channel
    insultees = arg_list[1:len(arg_list)]
    for x in range(len(insultees)):
        tosend = ""
        tosend += insultees[x]
        tosend += insults[random.randint(0, len(insults)-1)]
        await channel.send(tosend)
        print("insult sent")

# ---[ Run Bot ]---
client.run(TOKEN)
