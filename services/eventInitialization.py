from datetime import date, timedelta
import datetime
import discord
from utils.genericFunctions import get_season_and_game_id
import re


# region initialization function
async def event_initialization(schedule_Channel):
    today = date.today()

    messages = []
    async for message in schedule_Channel.history(limit=10):
        messages.append(message)

    embedded_data = messages[0].embeds[0]
    gameTime = int(re.search(r'\d+', str(embedded_data.fields[0].value)).group())

    legibleDateTime = datetime.datetime.utcfromtimestamp(gameTime) - timedelta(hours=4)

    print(legibleDateTime.date() < today)
    return
# endregion
