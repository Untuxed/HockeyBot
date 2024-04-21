from services.discordStuff import *
from services.firebaseStuff import *
from utils.genericFunctions import get_season_id


@tree.command(name='addnormie', description='Manually adds a Player to the Firestore db', guild=GUILD_ID)
async def addNormie(interaction: discord.Interaction,
                          first_name: str,
                          last_name: str,
                          number: str,
                          position: str,
                          status: str,
                          is_captain: bool,
                          handedness: str):
    player_id = f'{first_name}_{last_name}_{number}'
    season_id = get_season_id(interaction)

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
        if position == 'not specified':
            await interaction.response.send_message('No position role assigned.', ephemeral=True)
        if position == 'goalie':
            db.collection(season_id).document('roster').collection('goalies').document(player_id).set(player_data)
        else:
            db.collection(season_id).document('roster').collection('skaters').document(player_id).set(player_data)
        await interaction.response.send_message(content='Player added successfully.', ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f'An error occurred: {e}', ephemeral=True)