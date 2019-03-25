'''
Welcome to StockImageBot
A discord bot written in Python for StockImageSharks & N0ICE
'''

import discord
import discord.client
import random

# ---[ Bot Setup ]---
TOKEN = "Mzg5MTMxODA0NjI5NTMyNjcz.D3p31A.DF-0TaxP_5RiCEQ5547IcCjMt9o"
BOT_PREFIX = "}"

client = discord.Client()


@client.event
async def on_message(message):
    print(message.content)
    message_content = message.content.upper()
    # Bot should not reply to itself
    if message.author != client.user:

        # Check what command was and call appropriate function
        if BOT_PREFIX + "HELLO" in message_content:
            await client.send_message(message.channel, "working")

        # Roll dice
        elif BOT_PREFIX + "ROLL" in message_content:
            try:
                argList = message_content.split()
                await rollDice(message, argList[1], argList[2])
            except:
                print("Error rolling dice")

        # Flip a coin
        elif BOT_PREFIX + "FLIP" in message_content:
            flip = random.randint(1, 3)
            if flip == 1:
                await client.send_message(message.channel, "Heads")
            else:
                await client.send_message(message.channel, "Tails")

        elif BOT_PREFIX + "IAM" in message_content:
            argList = message_content.split()
            if argList[1] == "18+":
                role = discord.utils.get(message.server.roles, name="18+")
                await client.add_roles(message.author, role)
                await client.send_message(message.channel, "Over 18")
            elif argList[1] == "18-":
                await  message.channel.send("Under 18")


# ---[ Bot Commands ]---

async def rollDice(message, amount, size):
    amount = int(amount)
    size = int(size)

    if amount > 10:
        amount = 10
    if size > 100:
        size = 100

    for x in range(amount):
        i = random.randint(1, size)
        await client.send_message(message.channel, i)


# ---[ Run Bot ]---
client.run(TOKEN)
