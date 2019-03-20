'''
Welcome to StockImageBot
A discord bot written in Python for StockImageSharks & N0ICE
'''

from discord.ext.commands import Bot

TOKEN = ''
BOT_PREFIX = ''

client = Bot(command_prefix=BOT_PREFIX)

#---[ Bot Commands ]---

#---[ Run Bot ]---
client.run(TOKEN)