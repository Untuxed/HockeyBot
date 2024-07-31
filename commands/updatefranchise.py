from services.discordStuff import *
from services.firebaseStuff import *

@tree.command(
    name='updatefanchise',
    description='Update the franchise statistics',
    guild=GUILD_ID
)
async def syncdb(interaction: discord.Interaction):
    print('test')
