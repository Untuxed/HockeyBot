from services.firebaseStuff import db
import re
from datetime import datetime, timedelta



def checkDuplicatePlayer(collection_name: str, player_id: str):
    collection_ref = db.collection(collection_name).document(player_id)
    if collection_ref.get().exists:
        return True
    return False

async def get_player_data(first_name: str, last_name: str, number: str):
    # Get the player's data from Firestore
    playerID = f'{first_name}_{last_name}_{number}'  # stored as firstName_lastName_number in firestore
    player_ref = db.collection('statistics').document(playerID)  # get db reference
    player = player_ref.get()

    if not player.exists:
        return None

    player_data = player.to_dict()

    # Add these to the player_data dictionary
    player_data['first_name'] = first_name
    player_data['last_name'] = last_name
    player_data['number'] = number
    player_data['id'] = player.id
    return player_data


def generate_stats_message(player_data: dict):
    # Generate the stats message
    stats_message = f"Player: {player_data['first_name']} {player_data['last_name']}\n" \
                    f"Games Played: {player_data['gp']}\n" \
                    f"Goals: {player_data['goals']}\n" \
                    f"Assists: {player_data['assists']}\n" \
                    f"Points: {player_data['points']}\n" \
                    f"PPG: {player_data['ppg']}\n" \
                    f"PIMs: {player_data['pims']}"
    return stats_message


#region linebuilderv2 functions
def get_season_and_game_id(message):
    category_name = message.channel.category.name #season_id gets created from category name in discord
    season_id = re.sub(r'\s+', '_', category_name).lower()

    #get game information from embed to use as document id
    for embed in message.embeds:
        game_title = embed.title
        match = re.search(r':calendar_spiral:  \*\*Game (\d+) vs\. (.+?)\*\*', game_title)
        if match:
            game_number = match.group(1)
            opponent = match.group(2).replace(' ', '_')
        for field in embed.fields:
            if field.name == 'Time':
                match = re.search(r'<t:(\d+):F>', field.value)
                if match:
                    timestamp = int(match.group(1))
                    game_time = datetime.utcfromtimestamp(timestamp) - timedelta(hours=4)
                    formatted_time = game_time.strftime('%m-%d-%Y')
    
    doc_id = f'game_{game_number}_vs_{opponent}_{formatted_time}'
    return season_id, doc_id
#endregion