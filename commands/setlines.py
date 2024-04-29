from services.discordStuff import *
from utils.imageGenerator import imageGenerator, pullImage

@tree.command(
    name='setlines',
    description='Set lineup from the google sheet, generates lineup card image, responds with lineup card image.',
    guild=GUILD_ID
)
async def setLines(interaction: discord.Interaction):
    Lineup_File_Name = await imageGenerator(interaction)

    if not Lineup_File_Name:
        await interaction.followup.send('Something went wrong, looking into it.')

    Lineup_File_Name, _ = pullImage(interaction)

    if not Lineup_File_Name:
        await interaction.followup.send('Something went wrong, looking into it.')
    else:
        sent_message = await interaction.followup.send('**Latest Lineup Card**', file=discord.File(fp=Lineup_File_Name))
