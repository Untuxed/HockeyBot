from services.discordStuff import *
from services.firebaseStuff import *
from utils.genericFunctions import get_player_data, get_season_id
import re

@tree.command(name='addplayer', description='Adds a Player to the Firestore db', guild=GUILD_ID)
async def addPlayer(interaction: discord.Interaction, member: discord.Member):

    season_id = get_season_id(interaction)

    member_roles = member.roles

    number_match = re.search(r'\[(\d+)\]', str(member.display_name))
    if number_match:
        number = number_match.group(1)  # Extract the matched string
    else:
        number = None  # No number found

    first_name = str(member.display_name).split()[0]
    last_name = str(member.display_name).split()[1]
    
    position = 'not specified'
    status = 'friend of the program'
    is_captain = False
    handedness = 'not specified'

    if not first_name:
        await interaction.response.send_message('Invalid nickname format.')
        return

    player_id = f'{first_name}_{last_name}_{number}'

    for role in member_roles:
        role = str(role)
        if role == 'center':
            position = 'center'
        elif role == 'forward':
            position = 'forward'
        elif role == 'defense':
            position = 'defense'
        elif role == 'goalie':
            position = 'goalie'

        if role == f'{interaction.channel.category.name} Roster':
            status = 'rostered'
        elif role == 'substitute':
            status = 'substitute'
        elif role == 'retired':
            status = 'retired'

        if role == 'captain':
            is_captain = True

        if role == 'lefty':
            handedness = 'lefty'
        elif role == 'righty':
            handedness = 'righty'

    # set player info from roles
    player_data = {
        'discord_id': int(member.id),
        'number': int(number),
        'first_name': first_name,
        'last_name': last_name,
        'position': position,
        'status': status,
        'is_captain': is_captain,
        'handedness': handedness
    }

    try:
        if position == 'not specified':
            await interaction.response.send_message('No position role assigned.', ephemeral=True)
        if position == 'goalie':
            db.collection(season_id).document('roster').collection('goalies').document(player_id).set(player_data)
        else:
            db.collection(season_id).document('roster').collection('skaters').document(player_id).set(player_data)
        await interaction.response.send_message(content='Player added successfully.', ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f'An error occurred: {e}', ephemeral=True)