# BasicBot
# Code lifted from StockImage bot by meed223 with other minor contributors


import logging
import threading
import time
import typing
import functools
import asyncio

import discord
from regex import regex

import Commands

logging.basicConfig(filename="log.txt", level=logging.DEBUG, filemode="w")

# Global Variables

intents = discord.Intents.all()
client = discord.Client(intents=intents)
TOKEN = ""
BOT_PREFIX = ""
OP_USERFILE = "ops.cfg"


def setup():
    """ Get token & prefix from file and assigns to variables """
    file = open("token.txt", "r")
    global TOKEN
    TOKEN = file.readline().replace("\n", "")

    global BOT_PREFIX
    BOT_PREFIX = file.readline().replace("\n", "")
    file.close()
    logging.info(f"Bot token '{TOKEN}' and prefix '{BOT_PREFIX}' are set")


# ---[ Bot Event Code ]---
@client.event
async def on_ready():
    """ Set Discord Status """
    logging.info("Bot is Ready")
    print("Bot is Ready")
    await client.change_presence(status=discord.Status.idle,
                                 activity=discord.Activity(
                                     type=discord.ActivityType.playing,
                                     name="Starting bot!"))
    await presence_task()


async def presence_task():
    while True:
        if Commands.check_server_ping():
            await client.change_presence(status=discord.Status.online,
                                         activity=discord.Activity(
                                             type=discord.ActivityType.playing,
                                             name="Server is running :)"))
        else:
            await client.change_presence(status=discord.Status.do_not_disturb,
                                         activity=discord.Activity(
                                             type=discord.ActivityType.playing,
                                             name="Server is not running :("))
        await asyncio.sleep(15)


@client.event
async def on_message(message):
    """  This is run when a message is received on any channel """
    author = message.author
    o_args = message.content.split(' ')
    print(o_args[0])
    print(BOT_PREFIX)
    if author != client.user and o_args[0] == BOT_PREFIX:

        o_args[0] = o_args[0].replace(BOT_PREFIX, "")
        args = []
        for arg in o_args:
            if regex.search("[A-Z]+|[a-z]+|\d+", arg):
                args.append(arg)

        command = "help"
        if len(args) > 0:
            command = args[0].lower()
            del args[0]

        if command == "status":
            await Commands.server_status(message, True)
        elif command == "help":
            await Commands.bot_help(message, OP_USERFILE)
        elif command == "start_server":
            await Commands.start_server(message)
        elif command == "add_op":
            await Commands.add_op_user(message, args, OP_USERFILE)
        elif command == "remove_op":
            await Commands.remove_op_user(message, args, OP_USERFILE)


@client.event
async def on_member_join(member):
    """  New member joined server """
    print("member joined")


@client.event
async def on_guild_join(guild):
    """  Joined a new server """
    print("bot joined")


def is_authorized(message):
    """  Checks user privileges """
    authorized = False
    for member in message.guild.members:
        if member.id == message.author.id:
            # Check this ID specifically
            for r in member.roles:
                if r.permissions.manage_guild:
                    authorized = True
                    break
    return authorized


if __name__ == "__main__":
    try:
        setup()
        client.run(TOKEN)
    except FileNotFoundError:
        logging.error("File was not found, "
                      "are you sure that 'token.txt' exists?")
