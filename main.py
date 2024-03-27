import os
import re
import json
from tabulate import tabulate #do we still need this?
from datetime import datetime, timedelta #or this?
import time #or this?
from services.googleStuff import *
from services.discordStuff import *
from services.sheets import *
from utils.lineBuilder import *
from utils.lineBuilderv2 import *
from commands.firebaseSlashCommands import *
from dev.devTokens import discord_token_prod, discord_token_dev


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


hockeyBot.run(discord_token_dev)
