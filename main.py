from commands.firebaseSlashCommands import *
from services.googleStuff import *
from services.discordStuff import *
from services.sheets import *
from utils.lineBuilder import *
from utils.lineBuilderv2 import *
from services.eventInitialization import event_initialization
from dev.devTokens import discord_token_prod, discord_token_dev


@hockeyBot.event
async def on_ready():
    print(f'{hockeyBot.user.name} has connected to Discord!')

    await event_initialization(discord.utils.get(hockeyBot.guilds[1].text_channels, name='dev-schedule'))

    await tree.sync(guild=GUILD_ID)


hockeyBot.run(discord_token_dev)
