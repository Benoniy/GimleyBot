import os
from sys import platform
from rcon import Client
from datetime import datetime


async def bot_help(message, op_userfile):
    """ Provides a list of commands to the user """
    response = "```yaml\n" \
               "Standard_Commands:\n" \
               "    status: Shows the status of " \
               "the server\n"

    if str(message.author) in get_op_users(op_userfile):
        response += "--------------------------------------------\n\n" \
                    "OP_Commands:\n" \
                    "   start_server: Will start the server\n" \
                    "   add_op: Adds an op user, grants access to commands like start_server\n" \
                    "   remove_op: Removes an op user\n" \
                    "   save: Saves the game\n"

    response += "```"
    await message.channel.send(response)


def check_server_ping():
    hostname = "gimley"  # example
    try:
        if platform == "win32":
            response = os.system("ping -n 1 -w 100 " + hostname)
        else:
            response = os.system("ping -c 1 -W 1 " + hostname)
    except:
        response = 0

    # and then check the response...
    if response == 0:
        return True
    else:
        return False


def remove_non_ascii(string):
    return ''.join(char for char in string if ord(char) < 128)


def get_mc_server_details():
    rconPwd = open("rconPwd.cfg", "r").readline().strip("\n")
    online = False
    response = ""
    try:
        with Client('gimley', 25575, passwd=rconPwd) as client:

            seed = client.run('seed')[7:-2]

            server_ip = "stockimageshark.co.uk:25565"

            players = remove_non_ascii(client.run('list')).replace('6defaultr:', '').replace(",", "").strip(
                "\n").split(" ")
            current_players = players[2][1:-1]
            max_players = players[6][1:-1]
            del players[0:9]

            response += f"\nMinecraft Status: Online\n" \
                        f"Hostname: %s\n" \
                        f"World seed: %s\n" \
                        f"Players: %s/%s\n\n" \
                        f"" % (server_ip, seed, current_players, max_players)

            online = True
            if int(current_players) > 0:
                response += f"Players Online:\n"
                for player in players:
                    p = player[1:-2]
                    response += p + "\n"
    except:
        response += f"\nMinecraft Status: Offline"

    return {"status": online, "details": response}


async def server_status(message, send_message):
    response = check_server_ping()

    # and then check the response...
    if response:
        if send_message:


            response = f"```yaml\n" \
                       f"Server Status: Online\n" \
                       f"---------------------------------\n"

            response += get_mc_server_details()["details"]

            response += "```"
            await message.channel.send(response)
        #
        return True
    else:
        if send_message:
            response = f"```yaml\n" \
                       f"Status: Offline\n"

            response += "```"
            await message.channel.send(response)

        return False


async def start_server(message):
    if await server_status(message, False):
        await message.channel.send("Server is already running!")
    else:
        now = datetime.now().hour
        if 1 < now < 5:
            await message.channel.send("No go to sleep!")
        else:
            await message.channel.send("Starting server!")
            if platform != "win32":
                pass
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


async def save(message):
    rconPwd = open("rconPwd.cfg", "r").readline().strip("\n")

    try:
        with Client('gimley', 25575, passwd=rconPwd) as client:
            client.run('save-all')
    except:
        pass


async def unrecognised_command(message):
    await message.channel.send("no")


async def stop_server(message):
    rconPwd = open("rconPwd.cfg", "r").readline().strip("\n")
    try:
        with Client('gimley', 25575, passwd=rconPwd) as client:
            client.run('stop')
    except:
        pass
