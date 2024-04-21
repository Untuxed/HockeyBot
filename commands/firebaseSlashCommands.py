from services.discordStuff import *
import re
from tabulate import tabulate
import os
from utils.imageGenerator import imageGenerator, pullImage
from services.firebaseStuff import *
from utils.genericFunctions import checkDuplicatePlayer, get_player_data, generate_stats_message, get_game_date, get_season_and_game_id
import gspread
from services.sheets import *
from services.cellOperations import Range_Clear, get_players, Update_Cell_Range
import datetime


# region getmystats or just /mystats ????????
# TODO: Add a check for if player exists in the stats document, currently just breaks and throws a NoneType error
@tree.command(name='getmystats', description='Gets your stat card', guild=GUILD_ID)
async def getMyStats(interaction: discord.Interaction):
    # grab name and number from the user's nickname
    first_name, last_name, number = interaction.user.nick.replace('[', '').replace(']', '').split(' ')

    player = await get_player_data(first_name, last_name, number)
    stats_message = generate_stats_message(player)

    await interaction.response.send_message(stats_message, ephemeral=True)


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
        await interaction.response.send_message(stats_message, ephemeral=True)

    except ValueError:
        # If the player wasn't found, send an error message
        await interaction.response.send_message('Player does not exist.', ephemeral=True)


# endregion getplayerstats

# region set-lineup: pulls the lineup from the google sheet and displays them in the image form
@tree.command(
    name='set-lineup',
    description='Set lineup from the google sheet, generates lineup card image, responds with lineup card image.',
    guild=GUILD_ID
)
async def setLines(interaction: discord.Interaction):
    Lineup_File_Name = await imageGenerator(interaction)

    if not Lineup_File_Name:
        await interaction.followup.send('Something went wrong, looking into it.')

    Lineup_File_Name, _ = pullImage(interaction)

    if not Lineup_File_Name:
        await interaction.followup.send('Something went wrong, looking into it.')
    else:
        await interaction.followup.send('**Latest Lineup Card**', file=discord.File(fp=Lineup_File_Name))


# endregion set-lineup

# region get-lineup-new: pulls the current lines from the google sheet in image format
@tree.command(
    name='get-lineup',
    description='Gets image of the current lines.',
    guild=GUILD_ID
)
async def getLines(interaction: discord.Interaction):
    Lineup_File_Name, Dennis_Lineup_File_Name = pullImage(interaction)

    if not Lineup_File_Name:
        await interaction.followup.send_message('Something went wrong, looking into it.', ephemeral=True)
    elif not os.path.exists(Lineup_File_Name):
        await interaction.response.send_message('Lineup for the upcoming game not set yet.', ephemeral=True)
    elif int(interaction.user.id) == 1158794675558285385:
        await interaction.response.send_message('**Denny\'s Wittle Wineup Card**',
                                                file=discord.File(fp=Dennis_Lineup_File_Name), ephemeral=True)
    else:
        await interaction.response.send_message('**Latest Lineup Card**', file=discord.File(fp=Lineup_File_Name),
                                                ephemeral=True)


# endregion get-lineup-new

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

# region addplayer - adds a player to the roster and stats db
@tree.command(name='addplayer', description='Adds a Player to the Firestore db', guild=GUILD_ID)
async def addPlayer(interaction: discord.Interaction, member: discord.Member):
    await interaction.response.defer()
    category_name = interaction.channel.category.name  # season_id gets created from category name in discord
    season_id = re.sub(r'\s+', '_', category_name).lower()

    # Extract first name, last name, and number from the nickname
    match = re.match(r'(\w+)\s+(\w+)\s+\[(\d+)\]', member.nick)

    if not match:
        await interaction.response.send_message('Invalid nickname format.')
        return

    first_name, last_name, number = match.groups()
    playerID = f'{first_name}_{last_name}_{number}'

    # extract the roles from the member
    status = 'substitute' if any(role.name == 'Substitute' for role in member.roles) else 'rostered'

    is_captain = any(role.name == 'captain' for role in member.roles)

    valid_positions = ['center', 'forward', 'defenseman', 'goalie']
    position = next((role.name for role in member.roles if role.name in valid_positions), None)

    handedness = next((role.name[:-1] for role in member.roles if role.name in ['righty', 'lefty']), 'unknown')

    # set player info from roles
    player_data = {
        'discordID': str(member.id),
        'number': number,
        'first_name': first_name,
        'last_name': last_name,
        'position': position,
        'stats': status,
        'is_captain': is_captain,
        'handedness': handedness
    }

    try:
        if position == 'goalie':
            db.collection(season_id).document('roster').collection('goalies').document(playerID).set(player_data)
        else:
            db.collection(season_id).document('roster').collection('skaters').document(playerID).set(player_data)
        await interaction.followup.send('Player added successfully.')
    except Exception as e:
        await interaction.followup.send(f'An error occurred: {e}')


# endregion addplayer

# region manual-add-player #TODO: refactor this, probably broken
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
        'first_name': first_name,
        'last_name': last_name,
        'position': position,
        'status': status,
        'is_captain': is_captain,
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

# region getrsvps

@tree.command(name='importrsvps', description='Import RSVPs for a game', guild=GUILD_ID)
async def import_rsvps(interaction: discord.Interaction, game_id: str):
    # Define reference to correct db collection using the game id and season id
    season_id = interaction.channel.category.name.lower().replace(' ', '_')
    rsvp_ref = db.collection(season_id).document('games').collection(game_id).document('RSVPs')

    # Get the RSVP'd players for each category attendees, nos, and maybes
    rsvp_doc = rsvp_ref.get()
    if rsvp_doc.exists:
        rsvp_data = rsvp_doc.to_dict()
        attendees = rsvp_data.get('attendees', [])
        maybes = rsvp_data.get('maybes', [])
        nos = rsvp_data.get('nos', [])

        # Define the ranges
        attendees_range = 'Lineup!E3:E15'
        maybes_range = 'Lineup!F3:F15'
        nos_range = 'Lineup!G3:G15'

        # Clear the cells in the ranges
        Range_Clear([attendees_range, maybes_range, nos_range])

        # Write the RSVPs to the Google Sheet
        SHEET.values().update(spreadsheetId=VOODOO_SHEET_ID, range=attendees_range, valueInputOption='USER_ENTERED',
                              body={'values': [[name] for name in attendees]}).execute()
        SHEET.values().update(spreadsheetId=VOODOO_SHEET_ID, range=maybes_range, valueInputOption='USER_ENTERED',
                              body={'values': [[name] for name in maybes]}).execute()
        SHEET.values().update(spreadsheetId=VOODOO_SHEET_ID, range=nos_range, valueInputOption='USER_ENTERED',
                              body={'values': [[name] for name in nos]}).execute()

        await interaction.response.send_message(f"RSVPs for game {game_id} have been imported to the Google Sheet.")
    else:
        await interaction.response.send_message(f"No RSVPs found for game {game_id}.")


# endregion getrsvps

#region get game time

@tree.command(name='getgametime', description='Get the game time', guild=GUILD_ID)
async def get_game_time(interaction: discord.Interaction):
    next_game_date, next_game_time, opponent = get_game_date(interaction)

    if next_game_time is not None:
        ephemeral_message = f"NEXT GAME:\nvs. {opponent}\nDate: {next_game_date.strftime('%m-%d-%Y')}\nTime: {next_game_time}"
    else:
        ephemeral_message = "No upcoming games found."

    # Send the ephemeral message in the same channel where the command was invoked
    await interaction.response.send_message(content=ephemeral_message, ephemeral=True)
#endregion

# region avatar: goofy code
@tree.command(name="avatar", description="Get user avatar", guild=GUILD_ID)
async def avatar(interaction: discord.Interaction, member: discord.Member):
    await interaction.response.send_message(member.display_avatar)

# endregion avatar
