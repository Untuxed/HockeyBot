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
    base_URL, dennis_URL, _ = pullImage(interaction)
    
    season_id = get_season_id(interaction)
    
    if season_id == 'general':
        await interaction.response.send_message('This command cannot be used in general. Please use it in a team-specific channel.', ephemeral=True)
    
    if not base_URL:
        await interaction.response.send_message('Lineup for the upcoming game not set yet.', ephemeral=True)
    elif int(interaction.user.id) == 1158794675558285385:
        lineup_embed = discord.Embed(title='Lineup Embed Test 1', description='This is a test of the embed system')
        lineup_embed.set_image(url=dennis_URL)
        await interaction.response.send_message('**Denny\'s Wittle Wineup Card**', embed=lineup_embed, ephemeral=True)
    else:
        lineup_embed = discord.Embed(title='Lineup Embed Test 1', description='This is a test of the embed system')
        lineup_embed.set_image(url=base_URL)
        await interaction.response.send_message('**Latest Lineup Card**', embed=lineup_embed, ephemeral=True)
