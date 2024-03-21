from discordStuff import *
import re
from tabulate import tabulate
import os
from sheets import *
from cellOperations import get_player, get_players, generate_stats_message, Update_Cell_Range
from imageGenerator import imageGenerator, pullImage


# region get-my-stats: pulls your stats from the google sheet
@tree.command(name='get-my-stats', description='Views a players stats', guild=GUILD_ID)
async def getMyStats(interaction: discord.Interaction):
    # Get the sender's ID
    memberID = str(interaction.user.id)
    player = get_player(memberID)
    stats_message = generate_stats_message(player)
    await interaction.response.send_message(stats_message)


# endregion


# region get-player-stats
@tree.command(name='get-player-stats', description='Views all stats for a player', guild=GUILD_ID)
async def viewAllStats(interaction: discord.Interaction, member: discord.Member):
    # Get the desired player's ID
    memberID = str(member.id)

    try:
        # Try to get the player
        player = get_player(memberID)
        # If the player was found, send their stats
        stats_message = generate_stats_message(player)
        await interaction.response.send_message(stats_message)

    except ValueError:
        # If the player wasn't found, send an error message
        await interaction.response.send_message('Player does not exist.')


# endregion get-player-stats

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

    Lineup_File_Name = pullImage()

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
    Lineup_File_Name = pullImage()

    if not Lineup_File_Name:
        await interaction.response.send_message('Something went wrong, looking into it.')
    elif not os.path.exists(Lineup_File_Name):
        await interaction.response.send_message('Lineup for the upcoming game not set yet.')
    elif int(interaction.user.id) == 1158794675558285385:
        await interaction.response.send_message('**Denny\'s Wittle Wineup Card**', file=discord.File(fp=Lineup_File_Name))
    else:
        await interaction.response.send_message('**Latest Lineup Card**', file=discord.File(fp=Lineup_File_Name))


# endregion get-lineup-new

# region get-lineup-old: pulls the current lines from the google sheet
@tree.command(name='get-lines-old', description='(WIP) Gets the lineup from the google sheet', guild=GUILD_ID)
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


# region update-roster
@tree.command(name='update-roster', description='Adds a Player to the sheets db', guild=GUILD_ID)
async def addPlayer(interaction: discord.Interaction, member: discord.Member, gp: int = 0, goals: int = 0,
                    assists: int = 0, pims: int = 0):
    memberID = str(member.id)
    memberRoles = member.roles

    position = 'not-specified'
    status = 'friend-of-the-program'
    isCaptain = False
    handedness = 'not-specified'

    number = re.search(r'\[(\d+)\]', str(member.display_name))
    firstName = str(member.display_name).split()[0]
    lastName = str(member.display_name).split()[1]

    if not firstName or not lastName:
        firstName = ''
        lastName = ''

    if number:
        number = int(number.group(1))
    else:
        number = -1

    for role in memberRoles:
        role = str(role)
        if role == 'center':
            position = 'C'
        elif role == 'forward':
            position = 'F'
        elif role == 'defenseman':
            position = 'D'
        elif role == 'goalie':
            position = 'G'

        if role == 'Voodoo Baierl E1 Roster':
            status = 'fullTime'
        elif role == 'substitute':
            status = 'sub'

        if role == 'captain':
            isCaptain = True

        if role == 'lefty':
            handedness = 'left'
        elif role == 'righty':
            handedness = 'right'

    # Check if player already exists
    existing_players = SHEET.values().get(
        spreadsheetId=VOODOO_SHEET_ID, range=ROSTER_DB_RANGE_NAME).execute().get('values', [])
    existing_ids = [row[4] for row in existing_players if len(row) > 2]

    if memberID in existing_ids:
        await interaction.response.send_message('Player with that discord ID already exists.')
        return

    # Append new player to roster
    new_player = [number, firstName, lastName, position, memberID, status, isCaptain, handedness,
                  gp, goals, assists, goals + assists, (goals + assists) / gp if gp != 0 else 0, pims]
    SHEET.values().append(spreadsheetId=VOODOO_SHEET_ID, range=ROSTER_DB_RANGE_NAME, body={
        'values': [new_player]}, valueInputOption='RAW').execute()

    await interaction.response.send_message('Player added successfully.')


# endregion update-roster

# region avatar: goofy code
@tree.command(name="avatar", description="Get user avatar", guild=GUILD_ID)
async def avatar(interaction: discord.Interaction, member: discord.Member):
    await interaction.response.send_message(member.display_avatar)

# endregion avatar
