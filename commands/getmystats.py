from services.discordStuff import *
from utils.genericFunctions import get_player_data, generate_stats_message

@tree.command(name='getmystats', description='Gets your stat card', guild=GUILD_ID)
async def getMyStats(interaction: discord.Interaction):

    skater_stats_data, goalie_stats_data = await get_player_data(interaction)

    stats_message = generate_stats_message(skater_stats_data, goalie_stats_data)

    await interaction.response.send_message(stats_message, ephemeral=True)