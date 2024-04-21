from services.discordStuff import *
from utils.genericFunctions import get_player_data, generate_stats_message

@tree.command(name='getmystats', description='Gets your stat card', guild=GUILD_ID)
async def getMyStats(interaction: discord.Interaction):
    # grab name and number from the user's nickname
    first_name, last_name, number = interaction.user.nick.replace('[', '').replace(']', '').split(' ')

    player = await get_player_data(first_name, last_name, number)
    stats_message = generate_stats_message(player)

    await interaction.response.send_message(stats_message, ephemeral=True)