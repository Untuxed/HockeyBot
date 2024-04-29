from services.firebaseStuff import db
import re
import datetime


# region Check duplicate player 
def checkDuplicatePlayer(collection_name: str, player_id: str):
    collection_ref = db.collection(collection_name).document(player_id)
    if collection_ref.get().exists:
        return True
    return False
# endregion

# region Get player data for stats
async def get_player_data(interaction, first_name=None, last_name=None, number=None):
    if first_name is None:
        first_name, last_name, number = interaction.user.nick.replace('[', '').replace(']', '').split(' ')

    season_id = get_season_id(interaction)

    playerID = f'{first_name}_{last_name}_{number}'

    skater_stats_ref = db.collection(season_id).document('roster').collection('skaters').document(playerID)
    skater_data = skater_stats_ref.get().to_dict()

    goalie_stats_ref = db.collection(season_id).document('roster').collection('goalies').document(playerID)
    goalie_data = goalie_stats_ref.get().to_dict()

    if not skater_data or 'stats' not in skater_data:
        skater_stats_data = None
    
    if not goalie_data or 'stats' not in goalie_data:
        goalie_stats_data = None
    
    if skater_data is not None and 'stats' in skater_data:
        skater_stats_data = skater_data['stats']

        skater_stats_data['first_name'] = first_name
        skater_stats_data['last_name'] = last_name
        skater_stats_data['position'] = skater_data['position']
        skater_stats_data['number'] = number
    
    if goalie_data is not None and 'stats' in goalie_data:
        goalie_stats_data = goalie_data['stats']

        goalie_stats_data['first_name'] = first_name
        goalie_stats_data['last_name'] = last_name
        goalie_stats_data['position'] = goalie_data['position']
        goalie_stats_data['number'] = number

    return skater_stats_data, goalie_stats_data
# endregion

# region Generate stats message to send to the discord
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
# endregion

# region Linebuilderv2 functions
def get_season_and_game_id(message):
    season_id = get_season_id(message)

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

# region Get season ID
def get_season_id(messageish):
    category_name = messageish.channel.category.name 
    season_id = re.sub(r'\s+', '_', category_name).lower()
    return season_id
# endregion

# region Get next game date
def get_game_date(interaction):
    opponent = None 
    season_id = interaction.channel.category.name.lower().replace(' ', '_')
    games_db_ref = db.collection(season_id).document('games')

    today = datetime.date.today()

    next_game_time = None
    next_game_date = None

    for game in games_db_ref.collections():
        game_date_str = game.id 
        try:
            game_date = datetime.datetime.strptime(game_date_str, '%m-%d-%Y').date()
        except ValueError:
            continue

        if game_date >= today:
            game_info = game.document('game-info').get()

            if next_game_date is None or game_date < next_game_date:
                next_game_date = game_date
                next_game_time = datetime.datetime.strptime(game_info.get('gametime'), '%H:%M').strftime('%I:%M %p')
                opponent = game_info.get('opponent')

    return next_game_date, next_game_time, opponent
# endregion

# region Get full roster
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
# endregion

# region Get pending
def get_pending(attendees, maybes, nos, rosters):
    responded = attendees + maybes + nos

    popped_rosters = []

    for index, name in enumerate(rosters):
        if name in responded or name + ' ' + '[A]' in responded or name + ' ' + '[C]' in responded:
            continue
        else:
            popped_rosters.append(name)

    return popped_rosters
# endregion
