from services.discordStuff import *
import re
from tabulate import tabulate
import os
from utils.imageGenerator import imageGenerator, pullImage
from services.firebaseStuff import *
from utils.genericFunctions import checkDuplicatePlayer, get_player_data, generate_stats_message

db = firestore.client()

# region getmystats or just /mystats ????????
@tree.command(name='getmystats', description='Gets your stat card', guild=GUILD_ID)
async def getMyStats(interaction: discord.Interaction):
    # grab name and number from the user's nickname
    first_name, last_name, number = interaction.user.nick.replace('[', '').replace(']', '').split(' ')
    
    player = await get_player_data(first_name, last_name, number)
    stats_message = generate_stats_message(player)

    await interaction.response.send_message(stats_message)
# endregion getmystats

# region getplayerstats  or just /playerstats ????????
@tree.command(name='getplayerstats', description='Gets stats any player', guild=GUILD_ID)
async def getPlayerStats(interaction: discord.Interaction, member: discord.Member):
    # Get the desired player's ID
    first_name, last_name, number = member.nick.replace('[', '').replace(']', '').split(' ')

    try:
        # Try to get the player
        player = await get_player_data(first_name, last_name, number)
        # If the player was found, send their stats
        stats_message = generate_stats_message(player)
        await interaction.response.send_message(stats_message)

    except ValueError:
        # If the player wasn't found, send an error message
        await interaction.response.send_message('Player does not exist.')

# endregion getplayerstats

# region set-lineup: pulls the lineup from the google sheet and displays them in the image form
@tree.command(
    name='set-lineup',
    description='Set lineup from the google sheet, generates lineup card image, responds with lineup card image.',
    guild=GUILD_ID
)
async def setLines(interaction: discord.Interaction):
    Lineup_File_Name = imageGenerator()

    if not Lineup_File_Name:
        await interaction.response.send_message('Something went wrong, looking into it.')

    Lineup_File_Name, _ = pullImage()

    if not Lineup_File_Name:
        await interaction.response.send_message('Something went wrong, looking into it.')
    else:
        await interaction.response.send_message('**Latest Lineup Card**', file=discord.File(fp=Lineup_File_Name))


# endregion set-lineup

# region get-lineup-new: pulls the current lines from the google sheet in image format
@tree.command(
    name='get-lineup',
    description='Gets image of the current lines.',
    guild=GUILD_ID
)
async def getLines(interaction: discord.Interaction):
    Lineup_File_Name, Dennis_Lineup_File_Name = pullImage()

    if not Lineup_File_Name:
        await interaction.response.send_message('Something went wrong, looking into it.')
    elif not os.path.exists(Lineup_File_Name):
        await interaction.response.send_message('Lineup for the upcoming game not set yet.')
    elif int(interaction.user.id) == 1158794675558285385:
        await interaction.response.send_message('**Denny\'s Wittle Wineup Card**', file=discord.File(fp=Dennis_Lineup_File_Name))
    else:
        await interaction.response.send_message('**Latest Lineup Card**', file=discord.File(fp=Lineup_File_Name))


# endregion get-lineup-new

# region get-lineup-old: pulls the current lines from the google sheet
@tree.command(name='get-lines-old', description='(Depreciated) Gets the lineup from the google sheet', guild=GUILD_ID)
async def Lines(interaction: discord.Interaction):
    def generate_lineup_card(f, d, g):
        header = [["------", "Lineup Card", "------"]]
        underHeader = [["------", "-" * len(header[0][1]), "------"]]
        forwards_header = [["", "Forwards", ""], ["LW", "C", "RW"]]
        spacer = [
            ["------", "-" * len(header[0][1]), "------"]
        ]
        defense_header = [["", "Defense", ""], ["LD", "", "RD"]]
        goalie_header = [["", "Goalie", ""]]
        lineup_card = \
            header + underHeader + forwards_header + spacer + f + spacer + defense_header + spacer + d + spacer + \
            goalie_header + g
        return tabulate(lineup_card, stralign="center")

    forwardsRange = 'A5:C8'
    defenseRange = 'A11:C13'
    goalieRange = 'A16:C16'

    forwards = sheet.get(forwardsRange)
    defense = sheet.get(defenseRange)
    goalie = sheet.get(goalieRange)

    lineup = generate_lineup_card(forwards, defense, goalie)

    await interaction.response.send_message('```' + lineup + '```')


# endregion get-lineup-old

# region update-stats - adds stats from a single game to the stats sheet
@tree.command(name='update-stats', description='Increment a players stats', guild=GUILD_ID)
async def updateStats(interaction: discord.Interaction, member: discord.Member, goals: int = 0, assists: int = 0,
                      pims: int = 0, gp: int = 0):
    # Get the member's ID
    memberID = str(member.id)

    # Fetch all players from the Google Sheet
    players = get_players()

    # Find the player with the matching ID
    for i, player in enumerate(players):
        if player[4] == memberID:
            # Update the player's stats

            player[8] = gp  # Update GP

            player[8] = gp  # Update GP

            player[9] = int(player[9]) + goals  # Update goals
            player[10] = int(player[10]) + assists  # Update assists
            player[13] = int(player[13]) + pims  # Update PIMS
            player[11] = player[9] + player[10]  # Update total points
            player[12] = player[11] / player[8]  # Update average points per game

            # Update the player's stats in the Google Sheet

            await Update_Cell_Range(f'ROSTER DB!A{i + 2}:N{i + 2}', player)

            await interaction.response.send_message(f'Updated {player[1]} {player[2]}\'s stats.')
            return

    await interaction.response.send_message('Player ID does not exist.')


# endregion update-stats

# region addplayer TODO: clean up this code
@tree.command(name='addplayer', description='Adds a Player to the Firestore db', guild=GUILD_ID)
async def addPlayer(interaction: discord.Interaction, member: discord.Member):
    # Check if the user invoking the command has the 'captain' or 'admin' role
    if not any(role.name in ['captain', 'admin'] for role in interaction.user.roles):
        await interaction.response.send_message('You do not have permission to use this command.')
        return
    # Extract first name, last name, and number from the member's nickname
    match = re.match(r'(\w+)\s+(\w+)\s+\[(\d+)\]', member.nick)
    if not match:
        await interaction.response.send_message('Invalid nickname format. Nickname should be in the format "{firstName} {lastName} [{number}]"')
        return

    first_name, last_name, number = match.groups()
    playerID = f'{first_name}_{last_name}_{number}'

    # Determine the player's status, position, and captain status based on their roles
    status = 'substitute' if any(role.name == 'Substitute' for role in member.roles) else 'rostered'
    is_captain = any(role.name == 'captain' for role in member.roles)
    valid_positions = ['center', 'forward', 'defenseman', 'goalie']
    position = next((role.name for role in member.roles if role.name in valid_positions), None)
    handedness = 'right' if any(role.name == 'righty' for role in member.roles) else 'left'
    if not position:
        await interaction.response.send_message(f'Invalid position. Valid positions are: {", ".join(valid_positions)}')
        return
    
    roster_ref = db.collection('roster').document(playerID)
    if not await checkDuplicatePlayer(roster_ref):
        return

    # Add player to the roster
    roster_ref.set({
        'discordID': str(member.id),
        'number': number,
        'first-name': first_name,
        'last-name': last_name,
        'position': position,
        'status': status,
        'is-captain': is_captain,
        'handedness': handedness
    })

    # Check if player already exists in the statistics
    statistics_ref = db.collection('statistics').document(playerID)
    if statistics_ref.get().exists:
        await interaction.response.send_message('Player with that name and number already exists in the statistics.') #should we remove all these "confirmation" messages?
        return

    # Add player to the statistics
    statistics_ref.set({
        'gp': 0,
        'goals': 0,
        'assists': 0,
        'points': 0,
        'ppg': 0,
        'pims': 0
    })

    await interaction.response.send_message('Player added successfully.')
# endregion addplayer
    
# region manual-add-player
@tree.command(name='add-normie-player', description='Manually adds a Player to the Firestore db', guild=GUILD_ID)
async def addNormiePlayer(interaction: discord.Interaction, 
                          first_name: str, 
                          last_name: str, 
                          number: str, 
                          position: str, 
                          status: str, 
                          is_captain: bool, 
                          handedness: str):
    normieID = f'{first_name}_{last_name}_{number}'
    roster_ref = db.collection('roster').document(normieID)
    if not await checkDuplicatePlayer(roster_ref):
        return

    # Add player to the roster
    roster_ref.set({
        'number': number,
        'first-name': first_name,
        'last-name': last_name,
        'position': position,
        'status': status,
        'is-captain': is_captain,
        'handedness': handedness
    })

    # Check if player already exists in the statistics
    statistics_ref = db.collection('statistics').document(normieID)
    if statistics_ref.get().exists:
        await interaction.response.send_message('Player with that name and number already exists in the statistics.')
        return

    # Add player to the statistics
    statistics_ref.set({
        'gp': 0,
        'goals': 0,
        'assists': 0,
        'points': 0,
        'ppg': 0,
        'pims': 0
    })

    await interaction.response.send_message('Player added successfully.')
# endregion manual-add-player

# region avatar: goofy code
@tree.command(name="avatar", description="Get user avatar", guild=GUILD_ID)
async def avatar(interaction: discord.Interaction, member: discord.Member):
    await interaction.response.send_message(member.display_avatar)

# endregion avatar
