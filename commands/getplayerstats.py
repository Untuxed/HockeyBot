from services.discordStuff import *
from utils.genericFunctions import get_player_data, generate_stats_message

@tree.command(name='getplayerstats', description='Gets stats any player', guild=GUILD_ID)
async def getPlayerStats(interaction: discord.Interaction, member: discord.Member):
    # Get the desired player's ID
    name_parts = member.nick.replace('[', '').replace(']', '').split(' ')
    first_name, last_name, number = name_parts[:3]

    try:
        # Try to get the player
        player = await get_player_data(first_name, last_name, number)
        # If the player was found, send their stats
        stats_message = generate_stats_message(player)
        await interaction.response.send_message(stats_message, ephemeral=True)

    except ValueError:
        # If the player wasn't found, send an error message
        await interaction.response.send_message('Player does not exist.', ephemeral=True)
