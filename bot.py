'''
Welcome to StockImageBot
A discord bot written in Python for StockImageSharks & N0ICE
'''

import discord
import random

# ---[ Bot Setup ]---
TOKEN = "Mzg5MTMxODA0NjI5NTMyNjcz.D3sVag.ucJKODmE1y8oG5lvhYIhgHIeWOs"
BOT_PREFIX = "}"

client = discord.Client()


@client.event
async def on_ready():
    await client.change_presence(game=discord.Game(name="}help"))
    print("Dominatrix online\n")


@client.event
async def on_member_join(member):
    role = discord.utils.get(member.server.roles, name="Noobies")
    await client.add_roles(member, role)
    print("New member has joined")


# Happens whenever a message
@client.event
async def on_message(message):

    # Bot should not reply to itself and use the prefix
    if message.author != client.user and BOT_PREFIX in message.content:
        message_content = message.content.upper()
        arg_list = message_content.split()
        print(message_content)

        # Check what command was and call appropriate function
        if "STATUS" in arg_list[0]:
            await client.send_message(message.channel, "working")
            print("Printing status")

        # Roll dice
        elif "ROLL" in arg_list[0]:
            try:
                await roll_dice(message, arg_list[1], arg_list[2])
            except:
                print("Error rolling dice")

        # Flip a coin
        elif "FLIP" in arg_list[0]:
            flip = random.randint(1, 3)
            if flip == 1:
                await client.send_message(message.channel, "Heads")
                print("Heads")
            else:
                await client.send_message(message.channel, "Tails")
                print("Tails")

        elif "IAM" in arg_list[0]:
            await role_assign(message, arg_list)


# ---[ Bot Commands ]---
# Roles x amount of y sized dice
async def roll_dice(message, amount, size):
    amount = int(amount)
    size = int(size)

    if amount > 10:
        amount = 10
    if size > 100:
        size = 100

    for x in range(amount):
        i = random.randint(1, size)
        await client.send_message(message.channel, i)
        print("Rolled " + i)


async def role_assign(message, arg_list):

    # Only happens in server_guidelines
    if message.channel.name == "server_guidelines":
        temp_role = discord.utils.get(message.server.roles, name="Temp Members")

        # 18 or older
        if arg_list[1] == "18+":
            if "18-" in [y.name.lower() for y in message.author.roles]:
                role = discord.utils.get(message.server.roles, name="18-")
                await client.remove_roles(message.author, role)

            role = discord.utils.get(message.server.roles, name="18+")
            await client.add_roles(message.author, role)
            await client.send_message(message.channel, "Over 18")

        # Younger than 18
        elif arg_list[1] == "18-":
            if "18+" in [y.name.lower() for y in message.author.roles]:
                role = discord.utils.get(message.server.roles, name="18+")
                await client.remove_roles(message.author, role)
            role = discord.utils.get(message.server.roles, name="18-")
            await client.add_roles(message.author, role)
            await client.send_message(message.channel, "Under 18")

        # Remove noob role and add to temp members
        await client.remove_roles(message.author, discord.utils.get(message.server.roles, name="Noobies"))
        await client.add_roles(message.author, temp_role)
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
        await client.purge_from(message.channel, limit=100, check=is_admin)


# ---[ Run Bot ]---
client.run(TOKEN)
