import discord
from discord import app_commands
import json
import os

intents = discord.Intents.default()
intents.message_content = True
intents.guild_scheduled_events = True
intents.guilds = True
intents.members = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
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
        'PIMS': []
    }


@client.event
async def on_ready():
    print(f'{client.user.name} has connected to Discord!')
    await tree.sync(guild=GUILD_ID)


@client.event
async def on_message(message):
    if message.author == client.user.name:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

    if message.content.startswith('$lines'):
        await message.add_reaction("🤩")


@client.event
async def on_scheduled_event_create(event):
    if event:
        client.get_channel()


@client.event
async def on_scheduled_event_user_add(event, user):
    if user:
        print(user)


@tree.command(name='get-events', description='Test', guild=GUILD_ID)
async def getChannels(interaction: discord.Interaction):
    print(client.guilds[0].scheduled_events)

    subbedUsers = client.guilds[0].scheduled_events[0].users(limit=20, oldest_first=True)

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
    voodooTeam['PIMS'].append(pims)

    with open('./VoodooRoster.json', 'w') as f:
        f.write(json.dumps(voodooTeam))

    await interaction.response.send_message(voodooTeam)


@tree.command(name='view-stats', description='Views a players stats', guild=GUILD_ID)
async def viewStats(interaction: discord.Interaction, member: discord.Member, stat: str = None):
    memberID = member.id
    for i, ID in enumerate(voodooTeam['DISCORD USER ID']):
        if memberID == ID and stat.upper() in voodooTeam:
            await interaction.response.send_message(f'Player {voodooTeam["PLAYER NAME"][i]} has {voodooTeam[stat.upper()][i]} ' + stat.lower())
            return

    await interaction.response.send_message('Player or stat does not exist')


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


client.run('')
