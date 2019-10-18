'''
Welcome to StockImageBot
A discord bot written in Python for StockImageSharks & N0ICE
'''

# ---[ Imports ]---
import discord
import random
import math
import requests
from requests.exceptions import HTTPError
import json
from steam import SteamID


# ---[ Bot Setup ]---

# Actual bot token
TOKEN = "Mzg5MTMxODA0NjI5NTMyNjcz.D3sVag.ucJKODmE1y8oG5lvhYIhgHIeWOs"
BOT_PREFIX = "}"



# Testing bot token
'''
TOKEN = "NTU5ODk4NjI0MDg4MjExNDU2.D3u5fw.gVs5shbmR6_OysVkDnplpM1w3mk"
BOT_PREFIX = "{"
'''


rates = 0

client = discord.Client()


@client.event
async def on_ready():
    # get the JSON of currency rates - since RPi is supposed to reboot and re-run this each day, updating is a non-issue
    global rates
    try:
        response = requests.get("https://api.ratesapi.io/api/latest")
        rates = json.loads(response.text)
        rates = rates['rates']
        rates['EUR'] = 1  # Euro is default
        response.raise_for_status()  # throws exception if 404
    except HTTPError:
        print("Unsuccessful GET request for currency rates")
    except TypeError:
        print("Could not get dictionary from whatever was pulled.")
    # sets status of bot to ready/online when code is run
    game = discord.Game(" with your nipples")
    await client.change_presence(status=discord.Status.idle, activity=game, afk=False)
    print("Dominatrix online\n")

# ---[ Member Join Code ]---
@client.event
async def on_member_join(member):
    # Assigns 'noobies' role to a new member
    role = discord.utils.get(member.server.roles, name="Noobies")
    await member.add_roles(role, reason=None, atomic=True)
    print("New member has joined")

# ---[ Bot Command Code ]---
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

        # Print out modpacks used for games on the server
        elif arg_list[0] == BOT_PREFIX + "MODPACK" or arg_list[0] == BOT_PREFIX + "MODPACKS":
            tosend = ""
            tosend += "**Left-4-Dead-2:**\nhttps://steamcommunity.com/sharedfiles/filedetails/?id=1179844613\n"
            tosend += "**Golf with your Friends:**\nhttps://steamcommunity.com/sharedfiles/filedetails/?id=1565153035\n"
            tosend += "**Minecraft:**\nhttps://1drv.ms/u/s!AmQHrphd1TN71im1m0rEpudm4zrx?e=MH79yc\n"
            tosend += "**Garry's Mod:** (TTT)\nhttps://steamcommunity.com/sharedfiles/filedetails/?id=1737676630\n"
            tosend += "**Garry's Mod:** (Murder)\nhttps://steamcommunity.com/sharedfiles/filedetails/?id=1356744399\n"
            tosend += "**Team-Fortress 2:**\nhttps://steamcommunity.com/sharedfiles/filedetails/?id=1756023085\n"
            tosend += "**Space Engineers:** (Creative)\nhttps://steamcommunity.com/sharedfiles/filedetails/?id=1790802750\n"
            tosend += "**Space Engineers:** (Survival)\nhttps://steamcommunity.com/sharedfiles/filedetails/?id=1869425644\n"
            await channel.send(tosend)

        # Insult a member
        elif arg_list[0] == BOT_PREFIX + "INSULT":
            print("insult command recieved")
            try:
                await insult_gen(message, arg_list)
            except IndexError:
                await channel.send("You're the fool here! Try specifying someone to insult next time.")
                print("Error insulting, no user given to insult")
            except ValueError:
                await channel.send("Please @ someone to send an insult")
                print("Value Error in INSULT")

        # Seduce a member
        elif arg_list[0] == BOT_PREFIX + "SEDUCE":
            print("seduce command recieved")
            try:
                await seduce_gen(message, arg_list)
            except IndexError:
                await channel.send("Try specifying the person you'd like me to seduce.")
                print("Index Error in SEDUCE")
            except ValueError:
                await channel.send("Please @ someone to seduce")
                print("Value Error in SEDUCE")

        # Threaten a member
        elif arg_list[0] == BOT_PREFIX + "THREATEN":
            print("threaten command recieved")
            try:
                await threaten_gen(message, arg_list)
            except IndexError:
                await channel.send("Try specifying the person you'd like to threaten.")
                print("Index Error in THREATEN")
            except ValueError:
                await channel.send("Please @ someone to threaten")
                print("Value Error in THREATEN")

        elif arg_list[0] == BOT_PREFIX + "GOOGLE":
            try:
                await imageSearch(arg_list, message)
            except IndexError:
                await channel.send("Please give a search term.")

        # Convert an amount from one currency to another
        elif arg_list[0] == BOT_PREFIX + "CONVERT":
            print("Convert command recieved")
            if rates == 0:
                await channel.send("Exchange rate source unavailable right now. Try again tomorrow or after the bot has restarted.")
            try:
                await convert(message, arg_list)
            except IndexError:
                await channel.send("Index error. Either not enough arguments given or too many.")
                print("Index Error")
            except ValueError:
                await channel.send("Value error. Try using different currency codes")
                print("Value error")
            except KeyError:
                await channel.send("Key error. Try using different currency codes.")

        # Tell a user their roles
        elif arg_list[0] == BOT_PREFIX + "IAM":
            await role_assign(message, arg_list)

        # Generate teams
        elif arg_list[0] == BOT_PREFIX + "TEAMS":
            try:
                await team_gen(message, arg_list)
            except IndexError:
                await channel.send("Not enough arguments supplied, please see }help for instructions!")
                print("Error creating teams, not enough args")
            except ValueError:
                await channel.send("First argument can only be a number!")
                print("Error creating teams, type error")

        # Generate teams for Depth
        elif arg_list[0] == BOT_PREFIX + "TEAMS_SHARKS":
            try:
                await team_gen_sharks(message, arg_list)
            except IndexError:
                await channel.send("Not enough arguments supplied, please see }help for instructions!")
                print("Error creating teams, not enough args")
            except ValueError:
                await channel.send("First argument can only be a number!")
                print("Error creating teams, type error")

        # Help command
        elif arg_list[0] == BOT_PREFIX + "HELP":
            await send_help(message)

        # Steam ID Command
        elif arg_list[0] == BOT_PREFIX + "STEAMID":
            try:
                await getSteamID(arg_list, message)
            except IndexError:
                await channel.send("Not enough arguments supplied.")
                print("Index Error in SteamID")
            except ValueError:
                await channel.send("Not a valid username")

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
                            await channel.send("Not enough arguments supplied, please see }help for instructions!")
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
                       "sided dice\n}flip - Flips a coin\n}teams x @user @user... - Creates x "
                       "randomised teams containing any amount of users\n}teams_sharks @user "
                       "@user - shark selection for depth\n}insult @user - insults a user"
                       "\n}threaten @ user - threatens a user\n}seduce @user - seduces a user"
                       "\n}convert USD GBP amount - converts an amount from one currency to another")


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
    channel = message.channel
    print(author)
    # Only happens in server_guidelines
    temp_role = discord.utils.get(message.guild.roles, name="Temp Members")
    # 18 or older
    if arg_list[1] == "18+":
        print("18+")
        if "18-" in [y.name.lower() for y in message.author.roles]:
            role = discord.utils.get(message.guild.roles, name="Under 18")
            await author.remove_roles(role)
        role = discord.utils.get(message.guild.roles, name="18+")
        await author.add_roles(role)
        await channel.send("Over 18")
        print("role added")

    # Younger than 18
    elif arg_list[1] == "18-":
        if "18+" in [y.name.lower() for y in message.author.roles]:
            role = discord.utils.get(message.guild.roles, name="18+")
            await author.remove_roles(role)
            role = discord.utils.get(message.guild.roles, name="Under 18")
            await author.add_roles(role)
            await channel.send("Under 18")

    # Remove noob role and add to temp members
    noob_role = discord.utils.get(message.guild.roles, name="Noobies")
    await author.remove_roles(noob_role)
    await author.add_roles(temp_role)


# ---[ Bot Command Methods ]---
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
        await channel.purge(limit=100, check=is_admin)


async def purge_amount(message, limit):
    channel = message.channel
    await channel.purge_from(message.channel, limit=int(limit) + 1)


async def insult_gen(message, arg_list):
    # insults list
    insults = [" Your father was a hamster, and your mother smelled like elderberries!", " knows nothing!", " looks like Akif",
               " is a big smelly willy", " is no real super sand lesbian!", " thinks ketchup is spicy", " votes for trump",
               " is almost as mediocre at Overwatch as Akif", " lets face it, you're past your best at this point.", " is a troglodyte"]
    channel = message.channel
    insultees = arg_list[1:len(arg_list)]
    for x in range(len(insultees)):
        if "@" not in insultees[x]:
            raise ValueError('no @ symbol used')
        tosend = ""
        tosend += insultees[x]
        tosend += insults[random.randint(0, len(insults)-1)]
        await channel.send(tosend)
        print("insult sent")


async def seduce_gen(message, arg_list):
    # insults list
    seductions = [" I like your eyebrows.", " you look very HUMAN today", " let us abscond and create many sub-units together",
                  " my love for you is almost as strong as my hatred for Overwatch", " if I were human, I would kiss you.",
                  " if we work together, nothing will be able to stop us!"]
    channel = message.channel
    seducees = arg_list[1:len(arg_list)]
    for x in range(len(seducees)):
        if "@" not in seducees[x]:
            raise ValueError('no @ symbol used')
        tosend = ""
        tosend += seducees[x]
        tosend += seductions[random.randint(0, len(seductions) - 1)]
        await channel.send(tosend)
        print("seductions sent")


async def threaten_gen(message, arg_list):
    # threatens list
    threatens = [" I'll kill you!", " if God had wanted you to live, he would not have created me!",
                 "I can't legally practice law but I can take you down by the river with a crossbow to teach you a little something about god's forgotten children"]
    channel = message.channel
    threatenees = arg_list[1:len(arg_list)]
    for x in range(len(threatenees)):
        if "@" not in threatenees[x]:
            raise ValueError("No @ symbol used")
        tosend = ""
        tosend += threatenees[x]
        tosend += threatens[random.randint(0, len(threatens) - 1)]
        await channel.send(tosend)
        print("threatens sent")


async def convert(message, arg_list):
    # EUR = 1
    channel = message.channel
    toSend = ""
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
            toSend += "%.2f" % val + " in " + c1 + " is: "
            newval = val / float(rates[c1])
            newval *= float(rates[c2])
            toSend += "%.2f" % newval + " in " + c2
            await channel.send(toSend)
    else:
        raise IndexError("Too many or too few arguments")


async def getSteamID(arg_list, message):
    if len(arg_list) < 2 or len(arg_list) > 2: raise IndexError()
    tosend = ""
    channel = message.channel

    # Returns the different steam ID's for a given user
    id = SteamID.from_url("https://steamcommunity.com/id/" + arg_list[1] + "/")
    tosend += "SteamID: " + str(id.as_steam2_zero)
    tosend += "\nSteamID3: " + str(id.as_32)
    tosend += "\nSteamID64: " + str(id.as_64)
    tosend += "\n\n" + id.community_url

    await channel.send(tosend)

# ---[ Run Bot ]---
client.run(TOKEN)
