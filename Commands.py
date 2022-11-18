import os
from sys import platform


async def bot_help(message, op_userfile):
    """ Provides a list of commands to the user """
    response = "`status` - Shows the status of "\
               "the server\n"

    if str(message.author) in get_op_users(op_userfile):
        response += "`start_server` - Will start the server\n"\
                    "`add_op` - Adds an op user, grants access to commands like start_server\n"\
                    "`remove_op` - Removes an op user\n"

    await message.channel.send(response)


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


def get_op_users(op_userfile):
    file = open(op_userfile, "r")
    lines = file.readlines()
    ops = []
    for line in lines:
        ops.append(line.strip("\n"))

    return ops


async def add_op_user(message, args, op_userfile):
    ops = get_op_users(op_userfile)

    # Get all users
    user_list = []
    for member in message.guild.members:
        user_list.append(member.name + "#" + member.discriminator)

    if str(message.author) in ops:
        file = open(op_userfile, "a")

        for arg in args:
            if arg not in user_list:
                await message.channel.send(arg + " is not a user on this server!")

            elif arg in ops:
                await message.channel.send(arg + " is already op!")
            else:
                file.write(arg + "\n")
                await message.channel.send(arg + " added as op!")

        file.close()
    else:
        await message.channel.send("You do not have permission to add op users!")


async def remove_op_user(message, args, op_userfile):
    ops = get_op_users(op_userfile)

    if str(message.author) in ops:
        file = open(op_userfile, "w")

        for arg in args:
            if arg not in ops:
                await message.channel.send(arg + " is not an op user on this server!")

            elif arg in ops and arg != "Benoniy#1944":
                await message.channel.send(arg + " has been removes as an op user!")
                ops.remove(arg)

        for op in ops:
            file.write(op + "\n")
        file.close()
    else:
        await message.channel.send("You do not have permission to add op users!")

