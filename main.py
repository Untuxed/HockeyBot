import discord
from discord import app_commands
import json
import os
import pickle
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import re

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.guild_scheduled_events = True
intents.guilds = True
intents.members = True

scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(
    './hockeybot-417500-12b59baa2a04.json', scope
)

client = gspread.authorize(creds)
googleDoc = client.open('VoodooSpring2024Lineup')
sheet = googleDoc.get_worksheet(0)

hockeyBot = discord.Client(intents=intents)
tree = app_commands.CommandTree(hockeyBot)
GUILD_ID = discord.Object(id=107270946418622464)  # Personal server
GUILD_ID = discord.Object(id=1218284808552317009)  # Voodoo server

if os.path.isfile('./VoodooRoster.json'):
    with open('./VoodooRoster.json') as f:
        voodooTeam = json.loads(f.read())
else:
    voodooTeam = {
        'PLAYER NAME': [],
        'POSITION': [],
        'DISCORD USER ID': [],
        'GP': [],
        'GOALS': [],
        'ASSISTS': [],
        'POINTS': [],
        'PPG': [],
        'PIMS': []
    }


@hockeyBot.event
async def on_ready():
    print(f'{hockeyBot.user.name} has connected to Discord!')
    await tree.sync(guild=GUILD_ID)


@hockeyBot.event
async def on_message(message):
    if message.author == hockeyBot.user.name:
        return

    for embed in message.embeds:
        with open('object.pickle', 'wb') as f:
            pickle.dump(embed, f)

    if message.author == 'sesh':
        print(message)

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

    if message.content.startswith('$lines'):
        await message.add_reaction("🤩")


# TODO: get list of confirmed players from sesh message on edit
# TODO: add player to google sheet (yes's and maybe's, separate by position pref)
# TODO: save completed lines and then /command read from spreadsheet and create jpeg
@hockeyBot.event
async def on_message_edit(_, after):
    if str(after.author) == 'sesh#1244':
        sheet.batch_clear(["A2:A30"])
        attendees = after.embeds[0].fields[1].value
        attendees = re.findall(r'\d+', str(attendees))
        for i, id in enumerate(attendees):
            index = voodooTeam["DISCORD USER ID"].index(int(id))
            sheet.update_cell(i+2, 1, voodooTeam["PLAYER NAME"][index])


@hockeyBot.event
async def on_scheduled_event_create(event):
    if event:
        hockeyBot.get_channel()


@hockeyBot.event
async def on_scheduled_event_user_add(event, user):
    if user:
        print(user)


@tree.command(name='get-events', description='Test', guild=GUILD_ID)
async def getChannels(interaction: discord.Interaction):
    subbedUsers = hockeyBot.guilds[1].scheduled_events[0].users(limit=20, oldest_first=True)
    players = []

    async for u in subbedUsers:
        players.append(u.id)

    await interaction.response.send_message(players)


@tree.command(name="avatar", description="Get user avatar", guild=GUILD_ID)
async def avatar(interaction: discord.Interaction, member: discord.Member):
    await interaction.response.send_message(member.display_avatar)


@tree.command(name='add-player', description='Adds a Player to the roster', guild=GUILD_ID)
async def addPlayer(interaction: discord.Interaction, member: discord.Member, name: str = None, position: str = None, gp: int = 0, goals: int = 0, assists: int = 0, pims: int = 0):
    memberID = member.id
    for i in voodooTeam['DISCORD USER ID']:
        if memberID == i and len(voodooTeam) > 0:
            await interaction.response.send_message('Player with that discord ID already exists.')
            return

    voodooTeam['PLAYER NAME'].append(name)
    voodooTeam['POSITION'].append(position)
    voodooTeam['DISCORD USER ID'].append(memberID)
    voodooTeam['GP'].append(gp)
    voodooTeam['GOALS'].append(goals)
    voodooTeam['ASSISTS'].append(assists)
    voodooTeam['POINTS'].append(goals+assists)
    voodooTeam['PPG'].append((goals+assists)/gp)
    voodooTeam['PIMS'].append(pims)

    with open('./VoodooRoster.json', 'w') as f:
        f.write(json.dumps(voodooTeam))

    await interaction.response.send_message(voodooTeam)


@tree.command(name='view-stats', description='Views a players stats', guild=GUILD_ID)
async def viewStats(interaction: discord.Interaction, member: discord.Member, stat: str = None):
    memberID = member.id
    for i, ID in enumerate(voodooTeam['DISCORD USER ID']):
        if memberID == ID and stat.upper() in voodooTeam:
            await interaction.response.send_message(
                f'Player {voodooTeam["PLAYER NAME"][i]} has {voodooTeam[stat.upper()][i]} ' + stat.lower()
            )
            return

    await interaction.response.send_message('Player or stat does not exist')


@tree.command(name='sheet-clear-players', description='(WIP) Clears all players from RSVP list', guild=GUILD_ID)
async def clearRSVPs(interaction: discord.Interaction):
    sheet.batch_clear(["A2:A30"])
    await interaction.response.send_message('Cleared RSVP list, I hope you meant to do that.')


@tree.command(name='edit-stats', description='Edits a players stats', guild=GUILD_ID)
async def editStats(interaction: discord.Interaction, member: discord.Member, stat: str = None, new_value: str = None):
    memberID = member.id
    if not stat.upper() == 'PLAYER NAME' or not stat.upper() == 'POSITION':
        new_value = int(new_value)
    for i, ID in enumerate(voodooTeam['DISCORD USER ID']):
        if memberID == ID and stat.upper() in voodooTeam:
            oldStatValue = voodooTeam[stat.upper()][i]
            voodooTeam[stat.upper()][i] = new_value
            await interaction.response.send_message(
                'Changed ' + stat.lower() + f' from {oldStatValue} to {voodooTeam[stat.upper()][i]} for player '
                                            f'{voodooTeam["PLAYER NAME"][i]}')
            with open('./VoodooRoster.json', 'w') as f:
                f.write(json.dumps(voodooTeam))
            return

    await interaction.response.send_message('Player or stat does not exist')

# token
hockeyBot.run('')
