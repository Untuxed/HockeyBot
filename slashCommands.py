from discordStuff import *
import json
import os
import re
from tabulate import tabulate
from googleStuff import *
from sheets import *


# region avatar: goofy code
@tree.command(name="avatar", description="Get user avatar", guild=GUILD_ID)
async def avatar(interaction: discord.Interaction, member: discord.Member):
    await interaction.response.send_message(member.display_avatar)
# endregion avatar


# region get-my-stats: pulls your stats from the google sheet
@tree.command(name='get-my-stats', description='Views a players stats', guild=GUILD_ID)
async def getMyStats(interaction: discord.Interaction):
    # Get the member's ID
    memberID = str(interaction.user.id)

    # Fetch all players from the Google Sheet
    players = SHEET.values().get(spreadsheetId=VOODOO_SHEET_ID, range=ROSTER_DB_RANGE_NAME).execute().get('values', [])

    # Find the player with the matching ID
    player = next((player for player in players if player[4] == memberID), None)

    if player is None:
        # If the player wasn't found, send an error message
        await interaction.response.send_message('Player does not exist.')
    else:
        # If the player was found, send their stats
        number, firstName, lastName, position, memberID, status, isCaptain, handedness, gp, goals, assists, total, avg, pims = player
        stats_dict = {'GP': gp, 'GOALS': goals, 'ASSISTS': assists, 'TOTAL': total, 'PIMS': pims}
        stats_message = f'**Stats for {firstName} {lastName}:**\n'
        for stat_key, stat_value in stats_dict.items():
            stats_message += f'{stat_key}: {stat_value}\n'
        await interaction.response.send_message(stats_message)
# endregion


# region get-my-stats
@tree.command(name='get-player-stats', description='Views all stats for a player', guild=GUILD_ID)
async def viewAllStats(interaction: discord.Interaction, member: discord.Member):
    # Get the member's ID
    memberID = str(member.id)

    # Fetch all players from the Google Sheet
    players = SHEET.values().get(spreadsheetId=VOODOO_SHEET_ID, range=ROSTER_DB_RANGE_NAME).execute().get('values', [])

    # Find the player with the matching ID
    player = next((player for player in players if player[4] == memberID), None)

    if player is None:
        # If the player wasn't found, send an error message
        await interaction.response.send_message('Player does not exist.')
    else:
        # If the player was found, send their stats
        number, firstName, lastName, position, memberID, status, isCaptain, handedness, gp, goals, assists, total, avg, pims = player
        stats_dict = {'GP': gp, 'GOALS': goals, 'ASSISTS': assists, 'TOTAL': total, 'PIMS': pims}
        stats_message = f'**Stats for {firstName} {lastName}:**\n'
        for stat_key, stat_value in stats_dict.items():
            stats_message += f'{stat_key}: {stat_value}\n'
        await interaction.response.send_message(stats_message)
# endregion get-my-stats


# region get-lineup: pulls the current lines from the google sheet
@tree.command(name='lines', description='(WIP) Gets the lineup from the google sheet', guild=GUILD_ID)
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

    forwardsRange = 'A3:C6'
    defenseRange = 'A9:C12'
    goalieRange = 'A14:C14'

    forwards = sheet.get(forwardsRange)
    defense = sheet.get(defenseRange)
    goalie = sheet.get(goalieRange)

    lineup = generate_lineup_card(forwards, defense, goalie)

    await interaction.response.send_message('```' + lineup + '```')
# endregion get-lineup


# region update-stats - adds stats from a single game to the stats sheet
@tree.command(name='update-stats', description='Increment a players stats', guild=GUILD_ID)
async def updateStats(interaction: discord.Interaction, member: discord.Member, goals: int = 0, assists: int = 0, pims: int = 0, gp: int = 0):
    # Get the member's ID
    memberID = str(member.id)

    # Fetch all players from the Google Sheet
    players = SHEET.values().get(spreadsheetId=VOODOO_SHEET_ID, range=ROSTER_DB_RANGE_NAME).execute().get('values', [])

    # Find the player with the matching ID
    for i, player in enumerate(players):
        if player[4] == memberID:
            # Update the player's stats
            player[8] = gp # Update GP
            player[9] = int(player[9]) + goals  # Update goals
            player[10] = int(player[10]) + assists  # Update assists
            player[13] = int(player[13]) + pims  # Update PIMS
            player[11] = player[9] + player[10]  # Update total points
            player[12] = player[11] / player[8]  # Update average points per game

            # Update the player's stats in the Google Sheet
            SHEET.values().update(
                spreadsheetId=VOODOO_SHEET_ID,
                range=f'ROSTER DB!A{i+2}:N{i+2}',
                valueInputOption='USER_ENTERED',
                body={'values': [player]}
            ).execute()

            await interaction.response.send_message(f'Updated {player[1]} {player[2]}\'s stats.')
            return

    await interaction.response.send_message('Player ID does not exist.')
# endregion update-stats


# region update-roster
@tree.command(name='update-roster', description='Adds a Player to the sheets db', guild=GUILD_ID)
async def addPlayer(interaction: discord.Interaction, member: discord.Member, gp: int = 0, goals: int = 0, assists: int = 0, pims: int = 0):
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
                  gp, goals, assists, goals+assists, (goals+assists)/gp if gp != 0 else 0, pims]
    SHEET.values().append(spreadsheetId=VOODOO_SHEET_ID, range=ROSTER_DB_RANGE_NAME, body={
        'values': [new_player]}, valueInputOption='RAW').execute()

    await interaction.response.send_message('Player added successfully.')
# endregion update-roster


# region clear sheet
@tree.command(name='sheet-clear-players', description='DO NOT USE', guild=GUILD_ID)
async def clearRSVPs(interaction: discord.Interaction):
    botSheet.batch_clear(["A4:A19", "A21:A30"])
    await interaction.response.send_message('Cleared RSVP list, I hope you meant to do that.')
# endregion clear sheet
