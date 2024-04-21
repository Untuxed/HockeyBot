from services.discordStuff import *
from utils.imageGenerator import imageGenerator, pullImage
from utils.genericFunctions import get_season_id
import os

@tree.command(
    name='getlines',
    description='Gets image of the current lines.',
    guild=GUILD_ID
)
async def getLines(interaction: discord.Interaction):
    Lineup_File_Name, Dennis_Lineup_File_Name = pullImage(interaction)
    
    season_id = get_season_id(interaction)
    
    if season_id == 'general':
        await interaction.response.send_message('This command cannot be used in general. Please use it in a team-specific channel.', ephemeral=True)
    if not Lineup_File_Name:
        await interaction.response.send_message('Lineup for the upcoming game not set yet.', ephemeral=True)
    elif not os.path.exists(Lineup_File_Name):
        await interaction.response.send_message('Lineup for the upcoming game not set yet.', ephemeral=True)
    elif int(interaction.user.id) == 1158794675558285385:
        await interaction.response.send_message('**Denny\'s Wittle Wineup Card**',
                                                file=discord.File(fp=Dennis_Lineup_File_Name), ephemeral=True)
    else:
        await interaction.response.send_message('**Latest Lineup Card**', file=discord.File(fp=Lineup_File_Name),
                                                ephemeral=True)
