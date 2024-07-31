from services.discordStuff import *
from services.firebaseStuff import *
from utils.genericFunctions import get_player_data, get_season_id, player_id_from_discord_nickname
import re

@tree.command(name='addplayer', description='Adds a Player to the Firestore db', guild=GUILD_ID)
async def addPlayer(interaction: discord.Interaction, member: discord.Member):
    """
    Automatically adding a player to the firebase db based on a discrod username. The discord nickname must be in the format Firstname Lastname [number]. The code then uses discord roles to figure out the rest of the player information. This command can also splits players into two different roster groups 

    Parameters:
    - interaction (discord.Interaction): The discord interaction object from the command call.
    - member (discord.Member): The discord member to be added to the Firebase db.

    Returns:
    None
    """
    season_id = get_season_id(interaction)  # Get season ID from where the discord interaction.
    member_roles = member.roles  # Get's all of the roles that have been assigned to the member.

    first_name, last_name, number = player_id_from_discord_nickname(str(member.display_name))  # Gets the player's first name, last name, and number from discord ID
    
    # Default values for the role based arguments
    skater_position = 'not specified'
    goalie_position = 'not specified'
    status = 'friend of the program'
    is_captain = False
    handedness = 'not specified'

    # If the player is not formatted correctly return an error message to the user
    if not first_name or not last_name or not number:
        await interaction.response.send_message('Invalid nickname format.')
        return

    player_id = f'{first_name}_{last_name}_{number}'  # Form player ID for firebase

    # Loop for converting user roles to data in the firebase db
    for role in member_roles:
        role = str(role)  # Converts role to a string

        # If the player is a skater add their role to the skater role
        if role in ['center', 'defense', 'forward']:
            skater_position = role
        
        if role == 'goalie':
            goalie_position = role

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
        'status': status,
        'is_captain': is_captain,
        'handedness': handedness
    }

    try:
        if skater_position == 'not specified' and goalie_position == 'not specified':
            await interaction.response.send_message('No position role assigned.', ephemeral=True)

        if not goalie_position == 'not specified':
            player_data['position'] = 'goalie'
            player_doc = db.collection(season_id).document('roster').collection('goalies').document(player_id)
            player_info = player_doc.get()

            if not player_info.exists:
                player_doc.set(player_data)
            else:
                player_doc.update(player_data)

        if not skater_position == 'not specified':
            player_data['position'] = skater_position
            player_doc = db.collection(season_id).document('roster').collection('skaters').document(player_id)
            player_info = player_doc.get()

            if not player_info.exists:
                player_doc.set(player_data)
            else:
                player_doc.update(player_data)

        await interaction.response.send_message(content='Player added successfully.', ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f'An error occurred: {e}', ephemeral=True)
