from datetime import date
import discord
from utils.genericFunctions import get_season_and_game_id


# region initialization function
def event_initialization(GuildID):
    today = date.today()

    schedule_Channel_ID = discord.utils.get(get_guild.channels, name='dev-schedule')

    print(schedule_Channel_ID)

    # s_ID, event_date = get_season_and_game_id()

# endregion
