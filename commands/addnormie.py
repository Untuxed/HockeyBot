from services.discordStuff import *
from services.firebaseStuff import *
from utils.genericFunctions import get_season_id


@tree.command(name='addnormie', description='Manually adds a Player to the Firestore db', guild=GUILD_ID)
async def addNormie(interaction: discord.Interaction, first_name: str, last_name: str, number: str, position: str, status: str, is_captain: bool, handedness: str):
    """
    Manually creates a roster entry for a player in the Firestor database. 

    Parameters:
    - interaction (discord.Interaction): The discord interaction object from the command call.
    - first_name (str): Player's first name.
    - last_name (str): Player's last name.
    - number (str): Player's number.
    - position (str): Player's position (Center, Forward, Defense, and Goalie).
    - status (str): Player's status (rostered, substitute, friend-of-the-program).
    - is_captain (bool): Indicates whether the player is a team captain or not.
    - handedness (str): Player's handedness (lefty, righty).

    Returns:
    None
    """
    player_id = f'{first_name}_{last_name}_{number}'  # Creates the database ID for the player
    season_id = get_season_id(interaction)  # Gets the season ID from where the player was added

    # Creates the player dictionary for adding to the roster db
    player_data = {
        'discord_id': '',
        'number': int(number),
        'first_name': first_name,
        'last_name': last_name,
        'position': position,
        'status': status,
        'is_captain': is_captain,
        'handedness': handedness
    }

    try:
        # Check if position is not specified if there is not a position specified an error message is returned
        if position == 'not specified':
            await interaction.response.send_message('No position role assigned.', ephemeral=True)

        # Determine if the player is a goalie or a skater and assigns them to the correct roster db accordingly
        if position == 'goalie':
            db.collection(season_id).document('roster').collection('goalies').document(player_id).set(player_data)
        else:
            db.collection(season_id).document('roster').collection('skaters').document(player_id).set(player_data)
        
        # Success message
        await interaction.response.send_message(content='Player added successfully.', ephemeral=True)
    
    # If error return the error message to the discord server
    except Exception as e:
        await interaction.response.send_message(f'An error occurred: {e}', ephemeral=True)