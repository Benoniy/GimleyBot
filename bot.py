"""
BasicBot
Code lifted from StockImage bot by meed223 with other minor contributors
"""

from Commands import *

""" Global Variables """
client = discord.Client()
TOKEN = ""
BOT_PREFIX = ""


class Switcher(object):
    """ This switcher is based on the names of commands """
    def indirect(self, i, message, args):
        method = getattr(self, i, lambda: "invalid")
        return method(message, args)

    def help(self, message, args):
        return bot_help(message)

    def status(self, message, args):
        return message.channel.send("Bot is Online.")

    def roll(self, message, args):
        return roll_dice(message, args)

    def flip(self, message, args):
        return flip_coin(message)

    def teams(self, message, args):
        return team_gen(message, args)

    def ip(self, message, args):
        return get_ip(message)

    def announce(self, message, args):
        return announce(message, args)


def setup():
    """ Get token & prefix from file and assigns to variables """
    file = open("token.txt", "r")
    global TOKEN
    TOKEN = file.readline().replace("\n", "")

    global BOT_PREFIX
    BOT_PREFIX = file.readline().replace("\n", "")
    file.close()


# ---[ Bot Event Code ]---
@client.event
async def on_ready():
    """ Set Discord Status """
    print(f"Bot is running")
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="commands"))


@client.event
async def on_member_join(member):
    """  New member joined server """
    print("member joined")


@client.event
async def on_guild_join(guild):
    """  Joined a new server """
    print("bot joined")


@client.event
async def on_message(message):
    """  This is run when a message is received on any channel """
    author = message.author
    o_args = message.content.split(' ')

    if author != client.user and BOT_PREFIX in message.content:
        o_args[0] = o_args[0].replace(BOT_PREFIX, "")
        args = []

        for arg in o_args:
            if regex.search("[A-Z]+|[a-z]+|\d+", arg):
                args.append(arg)

        command = args[0].lower()
        del args[0]
        switch = Switcher()
        await switch.indirect(command, message, args)


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
        print("File was not found, are you sure that 'token.txt' exists?")
