# Stock Image Bot
A discord bot written in Python. Mainly for use by N0ice and StockImageSharks servers. The 'Stock Image' part of the name is a nonesense name, the bot has no stock-image related functionality.

## Usage:
### Setting-up a copy of this bot:
To setup your own version of this bot, you will need to get a bot-token from Discord, and add it to a text file called 'token.txt'  

You will also need to add the command prefix on the second line of the file. This is used to call bot commands  
i.e. `}` is one I use by default, so commands look like this: `}status`
## Files:
### bot2.py 
Version 2 of StockImageBot, this currently has most of the same commands as version 1, but links with an SQLite3 database to track user-text-channel activity and assigned roles more easily.
### bot2-db-build.py
This creates the database that is used by version 2 of the bot. This should be run whenever setting up the bot on a new machine.
## Old Code:
### build.sql
code used to build the SQLite3 database, this is now included in the build python file.
### bot.py 
Version 1 of StockImageBot, no longer active.
### meedbot.py
This is code for an old bot that no-longer functions. Was used to build version 1 of Stock Image Bot

## E-Ink Images
These are images to be used with an e-ink display, as part of a plan to set-up the bot to run on a Raspberry Pi 3.
The e-ink display will show that the bot is online / will display error codes / bot stats.