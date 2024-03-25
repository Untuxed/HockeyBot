# TODO: Fix usage with polls
# TODO: change getworksheet to be by name
# import json
# import os
import re
from tabulate import tabulate
from datetime import datetime, timedelta
import time
from services.googleStuff import *
from services.discordStuff import *
from services.sheets import *
# from slashCommands import *
from utils.lineBuilder import *
from commands.firebaseSlashCommands import *
from devs.devTokens import discord_token_dev


@hockeyBot.event
async def on_ready():
    print(f'{hockeyBot.user.name} has connected to Discord!')
    await tree.sync(guild=GUILD_ID)


@hockeyBot.event
async def on_scheduled_event_create(event):
    if event:
        hockeyBot.get_channel()


@hockeyBot.event
async def on_scheduled_event_user_add(event, user):
    if user:
        print(user)


# token
hockeyBot.run(discord_token_dev)
