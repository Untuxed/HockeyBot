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

    skater_stats_ref = db.collection(season_id).document('roster').collection('skaters').document(playerID)
    skater_data = skater_stats_ref.get().to_dict()

    goalie_stats_ref = db.collection(season_id).document('roster').collection('goalies').document(playerID)
    goalie_data = goalie_stats_ref.get().to_dict()

    if not skater_data or 'stats' not in skater_data:
        skater_stats_data = None
    
    if not goalie_data or 'stats' not in goalie_data:
        goalie_stats_data = None
    
    if skater_data is not None and 'stats' in skater_data:
        # Extract the stats data from the player data
        skater_stats_data = skater_data['stats']

        # Add these to the stats_data dictionary
        skater_stats_data['first_name'] = first_name
        skater_stats_data['last_name'] = last_name
        skater_stats_data['position'] = skater_data['position']
        skater_stats_data['number'] = number
    
    if goalie_data is not None and 'stats' in goalie_data:
        # Extract the stats data from the player data
        goalie_stats_data = goalie_data['stats']

        # Add these to the stats_data dictionary
        goalie_stats_data['first_name'] = first_name
        goalie_stats_data['last_name'] = last_name
        goalie_stats_data['position'] = goalie_data['position']
        goalie_stats_data['number'] = number

    return skater_stats_data, goalie_stats_data


def generate_stats_message(skater_stats_data: dict, goalie_stats_data: dict):
    stats_message = '\n'
    # Generate the stats message
    if skater_stats_data is not None:
        stats_message = stats_message + \
                        f"**Player**: {skater_stats_data['first_name']} {skater_stats_data['last_name']} (Position: {skater_stats_data['position']})\n" \
                        f"Games Played: {skater_stats_data['GP']}\n" \
                        f"Goals: {skater_stats_data['Goals']}\n" \
                        f"Assists: {skater_stats_data['Assists']}\n" \
                        f"Points: {skater_stats_data['Points']}\n" \
                        f"PPG: {skater_stats_data['PPG']}\n" \
                        f"Plus/Minus: {skater_stats_data['Plus/Minus']}\n" \
                        f"PIMs: {skater_stats_data['PIMs']}"
        
    if goalie_stats_data is not None:
        if not stats_message == '\n':
            stats_message = stats_message + '\n\n'

        stats_message = stats_message + \
                        f"**Player**: {goalie_stats_data['first_name']} {goalie_stats_data['last_name']} (Position: {goalie_stats_data['position']})\n" \
                        f"Games Played: {goalie_stats_data['GP']}\n" \
                        f"Goals Against: {goalie_stats_data['GA']}\n" \
                        f"Goals Against Average: {goalie_stats_data['GAA']}\n" \
                        f"Wins: {goalie_stats_data['Wins']}\n" \
                        f"Losses: {goalie_stats_data['Losses']}\n" \
                        f"PIMs: {goalie_stats_data['PIMs']}"
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
        rosteredSkaters.append(
            [int(playerDictionary['number']), playerDictionary['first_name'], playerDictionary['last_name']])

    for player in db.collection(season_id).document('roster').collection('goalies').stream():
        playerDictionary = player.to_dict()
        rosteredGoalies.append(
            [int(playerDictionary['number']), playerDictionary['first_name'], playerDictionary['last_name']])

    return rosteredSkaters, rosteredGoalies


def get_pending(attendees, maybes, nos, rosters):
    responded = []
    for item in attendees + maybes + nos:
        item = item.split(' ')
        responded.append([item[0] + ' ' + item[1] + ' ' + item[2]])

    pop_index = []

    for index, name in enumerate(rosters):
        playerID = [name[1] + ' ' + name[2] + f' [{name[0]}]']
        if playerID in responded:
            pop_index.append(index)

    pop_index.sort(reverse=True)

    [rosters.pop(index) for index in pop_index]

    popped_rosters = []

    for player in rosters:
        popped_rosters.append(player[1] + ' ' + player[2] + f' [{player[0]}]')

    return popped_rosters

