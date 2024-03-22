import discord
from discord import app_commands

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.guild_scheduled_events = True
intents.guilds = True
intents.members = True

# connection to discord server
hockeyBot = discord.Client(intents=intents)
tree = app_commands.CommandTree(hockeyBot)
GUILD_ID = discord.Object(id=107270946418622464)  # Personal server
GUILD_ID = discord.Object(id=1218284808552317009)  # Voodoo server
