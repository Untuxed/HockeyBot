from services.googleStuff import *
from services.discordStuff import *
from services.sheets import *
from utils.lineBuilder import *
from dev.devTokens import discord_token_prod, discord_token_dev
from commands.slashCommands import *

@hockeyBot.event
async def on_ready():
    print(f'{hockeyBot.user.name} has connected to Discord!')
    await tree.sync(guild=GUILD_ID)


hockeyBot.run(discord_token_dev)
