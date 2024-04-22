from services.firebaseStuff import db
import re
import datetime


def checkDuplicatePlayer(collection_name: str, player_id: str):
    collection_ref = db.collection(collection_name).document(player_id)
    if collection_ref.get().exists:
        return True
    return False


async def get_player_data(interaction, first_name=None, last_name=None, number=None):
    if first_name is None:
        first_name, last_name, number = interaction.user.nick.replace('[', '').replace(']', '').split(' ')

    season_id = get_season_id(interaction)

    # Get the player's data from Firestore
    playerID = f'{first_name}_{last_name}_{number}'  # stored as firstName_lastName_number in firestore
    stats_ref = db.collection(season_id).document('roster').collection('skaters').document(playerID)
    player_data = stats_ref.get().to_dict()

    if not player_data or 'stats' not in player_data:
        return None

    # Extract the stats data from the player data
    stats_data = player_data['stats']

    # Add these to the stats_data dictionary
    stats_data['first_name'] = first_name
    stats_data['last_name'] = last_name
    stats_data['number'] = number
    return stats_data


def generate_stats_message(stats_data: dict):
    # Generate the stats message
    stats_message = f"Player: {stats_data['first_name']} {stats_data['last_name']}\n" \
                    f"Games Played: {stats_data['GP']}\n" \
                    f"Goals: {stats_data['Goals']}\n" \
                    f"Assists: {stats_data['Assists']}\n" \
                    f"Points: {stats_data['Points']}\n" \
                    f"PPG: {stats_data['PPG']}\n" \
                    f"Plus/Minus: {stats_data['Plus/Minus']}\n" \
                    f"PIMs: {stats_data['PIMs']}"
    return stats_message

# region linebuilderv2 functions
def get_season_and_game_id(message):
    season_id = get_season_id(message)

    # get game information from embed to use as document id
    if message.embeds:
        game_title = message.embeds[0].title
        match = re.search(r':calendar_spiral: (.+)', game_title)
        time_field = message.embeds[0].fields[0]
        if match:
            opponent = match.group(1)
        if time_field.name == 'Time':
            match = re.search(r'<t:(\d+):F>', time_field.value)
            if match:
                timestamp = int(match.group(1))
                game_time = datetime.datetime.utcfromtimestamp(timestamp) - datetime.timedelta(hours=4)
                formatted_time = game_time.strftime('%m-%d-%Y')
                gametime = game_time.strftime('%H:%M')

    game_id = f'{formatted_time}'
    return season_id, game_id, gametime, opponent
# endregion

def get_season_id(messageish):
    category_name = messageish.channel.category.name  # season_id gets created from category name in discord
    season_id = re.sub(r'\s+', '_', category_name).lower()
    return season_id

# region finding dates from firebase
def get_game_date(interaction):
    opponent = None 
    season_id = interaction.channel.category.name.lower().replace(' ', '_')
    games_db_ref = db.collection(season_id).document('games')

    # Get today's date
    today = datetime.date.today()

    # Initialize the next game time and date
    next_game_time = None
    next_game_date = None

    # Iterate over all game collections
    for game in games_db_ref.collections():
        game_date_str = game.id  # The collection id is the game date in mm-dd-yyyy format

        # Check if the document id can be parsed as a date
        try:
            game_date = datetime.datetime.strptime(game_date_str, '%m-%d-%Y').date()
        except ValueError:
            continue  # Skip this document if its id cannot be parsed as a date
        # Check if the game date is in the future
        if game_date >= today:
            # Get the game info
            game_info = game.document('game-info').get()

            # Check if this game is earlier than the currently found next game
            if next_game_date is None or game_date < next_game_date:
                next_game_date = game_date
                next_game_time = datetime.datetime.strptime(game_info.get('gametime'), '%H:%M').strftime('%I:%M %p')
                opponent = game_info.get('opponent')  # Get the opponent

    return next_game_date, next_game_time, opponent


# endregion

# region, get full roster
def get_roster(interaction):
    season_id = get_season_id(interaction)

    rosteredSkaters = []
    rosteredGoalies = []

    for player in db.collection(season_id).document('roster').collection('skaters').stream():
        playerDictionary = player.to_dict()
        number = playerDictionary['number']
        rosteredSkaters.append(playerDictionary['first_name'] + ' ' + playerDictionary['last_name'] + f' [{number}]')

    for player in db.collection(season_id).document('roster').collection('goalies').stream():
        playerDictionary = player.to_dict()
        number = playerDictionary['number']
        rosteredSkaters.append(playerDictionary['first_name'] + ' ' + playerDictionary['last_name'] + f' [{number}]')

    return rosteredSkaters, rosteredGoalies


def get_pending(attendees, maybes, nos, rosters):
    responded = attendees + maybes + nos

    popped_rosters = []

    for index, name in enumerate(rosters):
        if name in responded or name + ' ' + '[A]' in responded or name + ' ' + '[C]' in responded:
            continue
        else:
            popped_rosters.append(name)

    return popped_rosters

