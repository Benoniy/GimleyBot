import os
from sys import platform


async def bot_help(message):
    """ Provides a list of commands to the user """
    await message.channel.send("`}status` - Shows the status of "
                               "the server\n"
                               )


async def server_status(message, send_message):
    hostname = "gimley"  # example
    if platform == "win32":
        response = os.system("ping -n 1 " + hostname)
    else:
        response = os.system("ping -c 1 " + hostname)

    # and then check the response...
    if response == 0:
        if send_message:
            await message.channel.send("Server is up")
        return True
    else:
        if send_message:
            await message.channel.send("Server is down")
        return False


async def start_server(message):
    if await server_status(message, False):
        await message.channel.send("Server is already running!")
    else:
        await message.channel.send("Starting server!")
        if platform != "win32":
            os.system('wakeonlan 40:16:7e:ad:19:bc')


# announcement command
async def announce(message, args):
    # announce_channel = discord.utils.get(message.guild.text_channels,
    #                                      name="general-tomfoolery")
    tosend = "**<@" + str(message.author.id) + "> would like to announce:**\n"

    try:
        for i in range(0, len(args)):
            tosend += args[i] + " "
        tosend += "\n*this message will be deleted " \
                  "automatically  in 30 minutes*"

        await message.channel.send("Message will be announced in "
                                   "#General-Tomfoolery and deleted 30 "
                                   "minutes from now.")
    except IndexError:
        await message.channel.send("Please write a message. If you think "
                                   "you used this command correctly, "
                                   "consult the help command or ask "
                                   "Henry for help.")
