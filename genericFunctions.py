from firebaseStuff import db

async def checkDuplicatePlayer(collection_ref: str):
    # collection_ref = db.collection(collection_name).document(player_id)
    if collection_ref.get().exists:
        return True
    return False

async def get_player(memberID: str):
    # Get the player's data from Firestore
    player_ref = db.collection('statistics').document(memberID)
    player = player_ref.get()

    if not player.exists:
        return None

    return player.to_dict()

def generate_stats_message(player_data: dict, sender_id = None):
    if sender_id:
        first_name, last_name, number = sender_id.split(' ')
    # Generate the stats message
    stats_message = f"Player: {first_name} {last_name}\n" \
                    f"Games Played: {player_data['gp']}\n" \
                    f"Goals: {player_data['goals']}\n" \
                    f"Assists: {player_data['assists']}\n" \
                    f"Points: {player_data['points']}\n" \
                    f"PPG: {player_data['ppg']}\n" \
                    f"PIMs: {player_data['pims']}"
    return stats_message