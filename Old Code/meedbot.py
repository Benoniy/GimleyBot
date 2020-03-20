#Code written by Meed223
#Based off various tutorials for using Discord API
import random
from discord import Game
from discord.ext.commands import Bot

BOT_PREFIX = ('>')
# TOKEN removed as it is flagged up due to public git.

client = Bot(command_prefix=BOT_PREFIX)

@client.command(
                #Pick a colour to play as for AoE, include command alias'
                name='colour',
                description="Picks a team colour for player",
                brief="Picks a team colour.",
                aliases=['color', 'colourpick', 'colorpick', 'whatcolour', 'whatcolor',],
                pass_context=False
                )
async def eight_ball():
    possible_colours = [
        '1. Blue',
        '2. Red',
        '3. Green',
        '4. Yellow'
        '5. Cyan',
        '6. Pink',
        '7. Grey',
        '8. Orange',
    ]
    await client.say(random.choice(possible_colours))

@client.command(
                name='whatciv',
                description="Randomly selects a civilisation to play as in Civ V",
                brief='Picks a civ',
                aliases=['civ',],
                pass_context=True
)
async def whatciv(context):
    # Generate list of possible empires to play as (from Civ V)
    possible_responses = [
        'This day ' + context.message.author.mention + ' shall be the ',
        context.message.author.mention + ' is going to be the ',
        "Make 'em proud " + context.message.author.mention + " you're the ",
        context.message.author.mention + ' may your conquest be great, you get to play as the ',
    ]
    possible_civs = [
        'Americans',
        'Arabians',
        'Assyrians',
        'Austrian',
        'Aztec',
        'Babylonian',
        'Brazilian',
        'Byzantine',
        'Carthagian',
        'Celtic',
        'Chinese',
        'Danish',
        'Dutch',
        'Egyptian',
        'English',
        'Ethiopian',
        'French',
        'German',
        'Greek',
        'Hunnic',
        'Incan',
        'Indian',
        'Indonesian',
        'Iroquois',
        'Japanese',
        'Korean',
        'Mayan',
        'Mongolian',
        'Moroccan',
        'Ottoman',
        'Persian',
        'Polish',
        'Polynesian',
        'Roman',
        'Russian',
        'Shoshone',
        'Siamese',
        'Songhai',
        'Spanish',
        'Swedish',
        'Venetian',
        'Zulu',
    ]
    await client.say(random.choice(possible_responses) + random.choice(possible_civs))

@client.command(
                name='whatempire',
                description="Randomly selects a civilisation to play as in age of empires.",
                brief='Picks a empire',
                aliases=['empire','whoshouldibe',],
                pass_context=True
)
async def whatempire(context):
    #Generate list of possible empires to play as (from AoE2)
    possible_responses = [
        'This day ' + context.message.author.mention + ' shall be the ',
        context.message.author.mention + ' is going to be the ',
        "Make 'em proud " + context.message.author.mention + " you're the ",
        context.message.author.mention + ' may your conquest be great, you get to play as the ',
    ]
    possible_empires = [
        'Aztecs',
        'Berbers',
        'Britons',
        'Burmese',
        'Byzantines',
        'Celts',
        'Chinese',
        'Ethiopians',
        'Franks',
        'Goths',
        'Huns',
        'Incas',
        'Indians',
        'Italians',
        'Japanese',
        'Khmer',
        'Koreans',
        'Magyars',
        'Malay',
        'Malians',
        'Mongols',
        'Persians',
        'Portugese',
        'Saracens',
        'Slavs',
        'Spanish',
        'Teutons',
        'Turks',
        'Vietnamese',
        'Vikings',
    ]
    await client.say(random.choice(possible_responses) + random.choice(possible_empires))

@client.command(
                #Info about command, inc. command alias'
                name='taunt',
                description="Taunts user with text-taunt from Age of Empires 2.",
                brief="Taunts the user.",
                aliases=['aoetaunt','tauntme'],
                pass_context=True
                )
async def taunt(context):
    #List of AoE2 Taunts printed to text channel
    possible_responses = [
        'Yes.',
        'No.',
        'Food please.',
        'Wood please.',
        'Gold please.',
        'Stone please.',
        'Ahh!',
        'All hail, king of the losers!',
        'Ooh!',
        "I'll beat you back to Age of Empires.",
        '(Herb laugh)',
        'Ah! Being rushed.',
        'Sure, blame it on your ISP.',
        'Start the game already!',
        "Don't point that thing at me!",
        'Enemy sighted!',
        'It is good to be the king.',
        'Monk! I need a monk!',
        'Long time, no siege.',
        'My granny could scrap better than that.',
        "Nice town, I'll take it.",
        'Quit touching me!',
        'Raiding party!',
        'Dadgum',
        'Eh, smite me',
        'The wonder, the wonder, the... no!',
        'You played two hours to die like this?',
        'Yeah, well, you should see the other guy.',
        'Roggan.',
        'Wololo.',
        'Attack an enemy now.',
        'Cease creating extra villagers.',
        'Create extra villagers.',
        'Build a navy.',
        'Stop building a navy.',
        'Wait for my signal to attack.',
        'Build a wonder.',
        'Give me your extra resources.',
        '(Ally sound)',
        '(Enemy sound)',
        '(Neutral sound)',
        'What age are you in?',
    ]
    await client.say(context.message.author.mention + ", " + random.choice(possible_responses))

@client.command()
async def square(number):
    squared_value = int(number) * int(number)
    await client.say(str(number) + " squared is " + str(squared_value))


@client.event
async def on_ready():
    await client.change_presence(game=Game(name="Ready"))
    print("Logged in as " + client.user.name)

client.run(TOKEN)