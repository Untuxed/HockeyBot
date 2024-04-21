from services.discordStuff  import *
from utils.genericFunctions import get_game_date, get_season_id

@tree.command(name='getgametime', description='Get the game time', guild=GUILD_ID)
async def getGameTime(interaction: discord.Interaction):
    next_game_date, next_game_time, opponent = get_game_date(interaction)
    
    season_id = get_season_id(interaction)

    if season_id == 'general':
        ephemeral_message = 'This command cannot be used in general. Please use it in a team-specific channel.'
    elif next_game_time is not None:
        ephemeral_message = f"NEXT GAME:\nvs. {opponent}\nDate: {next_game_date.strftime('%m-%d-%Y')}\nTime: {next_game_time}"
    else:
        ephemeral_message = "No upcoming games found."

    # Send the ephemeral message in the same channel where the command was invoked
    await interaction.response.send_message(content=ephemeral_message, ephemeral=True)
