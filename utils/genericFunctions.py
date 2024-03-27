from services.firebaseStuff import db


def checkDuplicatePlayer(collection_name: str, player_id: str):
    collection_ref = db.collection(collection_name).document(player_id)
    if collection_ref.get().exists:
        return True
    return False

async def get_player_data(first_name: str, last_name: str, number: str, season: str):
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
