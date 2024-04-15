from commands.firebaseSlashCommands import *
from dev.devTokens import discord_token_prod, discord_token_dev


@hockeyBot.event
async def on_ready():
    print(f'{hockeyBot.user.name} has connected to Discord!')
    await tree.sync(guild=GUILD_ID)


hockeyBot.run(discord_token_dev)
