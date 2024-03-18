from discordStuff import *
import json
import os
import re
from googleStuff import *
from sheets import *


@tree.command(name='get-events', description='Test', guild=GUILD_ID)
async def getChannels(interaction: discord.Interaction):
    subbedUsers = hockeyBot.guilds[1].scheduled_events[0].users(
        limit=20, oldest_first=True)
    players = []

    async for u in subbedUsers:
        players.append(u.id)

    await interaction.response.send_message(players)


# what's this do?
@tree.command(name="avatar", description="Get user avatar", guild=GUILD_ID)
async def avatar(interaction: discord.Interaction, member: discord.Member):
    await interaction.response.send_message(member.display_avatar)



@tree.command(name='view-stats', description='Views a players stats', guild=GUILD_ID)
async def viewStats(interaction: discord.Interaction, member: discord.Member, stat: str = None):
    memberID = member.id
    for i, ID in enumerate(voodooTeam['DISCORD USER ID']):
        if memberID == ID and stat.upper() in voodooTeam:
            await interaction.response.send_message(
                f'Player {voodooTeam["PLAYER NAME"][i]} has {voodooTeam[stat.upper()][i]} ' +
                stat.lower()
            )
            return

    await interaction.response.send_message('Player or stat does not exist')


# returns stats for whoever uses the command
@tree.command(name='view-my-stats', description='Views all your own stats', guild=GUILD_ID)
async def viewMyStats(interaction: discord.Interaction):
    memberID = interaction.user.id  # Get the ID of the interaction's user
    for i, ID in enumerate(voodooTeam['DISCORD USER ID']):
        if memberID == ID:
            player_name = voodooTeam['PLAYER NAME'][i]
            stats_message = f'**Stats for {player_name}:**\n'
            for stat_key, stat_values in voodooTeam.items():
                if stat_key.upper() not in ('DISCORD USER ID', 'PLAYER NAME'):
                    if stat_key.upper() in ('GP', 'GOALS', 'ASSISTS', 'POINTS', 'PIMS'):
                        if i < len(stat_values):
                            stats_message += f'{stat_key}: {stat_values[i]}\n'
                        else:
                            stats_message += f'{stat_key}: [No data]\n'
            await interaction.response.send_message(stats_message)
            return

    await interaction.response.send_message('Player not found')


# returns stats for the specified player
@tree.command(name='view-player-stats', description='Views all stats for a player', guild=GUILD_ID)
async def viewAllStats(interaction: discord.Interaction, member: discord.Member):
    memberID = member.id
    for i, ID in enumerate(voodooTeam['DISCORD USER ID']):
        if memberID == ID:
            player_name = voodooTeam['PLAYER NAME'][i]
            stats_message = f'**Stats for {player_name}:**\n'
            for stat_key, stat_values in voodooTeam.items():
                if stat_key.upper() not in ('DISCORD USER ID', 'PLAYER NAME'):
                    if stat_key.upper() in ('GP', 'GOALS', 'ASSISTS', 'POINTS', 'PIMS'):
                        if i < len(stat_values):
                            stats_message += f'{stat_key}: {stat_values[i]}\n'
                        else:
                            stats_message += f'{stat_key}: [No data]\n'
            await interaction.response.send_message(stats_message)
            return

    await interaction.response.send_message('Player not found')


@tree.command(name='sheet-clear-players', description='DO NOT USE', guild=GUILD_ID)
async def clearRSVPs(interaction: discord.Interaction):
    botSheet.batch_clear(["A4:A19", "A21:A30"])
    await interaction.response.send_message('Cleared RSVP list, I hope you meant to do that.')


@tree.command(name='get-lineup', description='(WIP) Gets the lineup from the google sheet', guild=GUILD_ID)
async def getLineup(interaction: discord.Interaction):
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


@tree.command(name='edit-stats', description='Edits a players stats', guild=GUILD_ID)
async def editStats(interaction: discord.Interaction, member: discord.Member, stat: str = None, new_value: str = None):
    memberID = member.id
    if not stat.upper() == 'PLAYER NAME' or not stat.upper() == 'POSITION':
        new_value = int(new_value)
    for i, ID in enumerate(voodooTeam['DISCORD USER ID']):
        if memberID == ID and stat.upper() in voodooTeam:
            oldStatValue = voodooTeam[stat.upper()][i]
            voodooTeam[stat.upper()][i] = new_value
            await interaction.response.send_message(
                'Changed ' + stat.lower() +
                f' from {oldStatValue} to {voodooTeam[stat.upper()][i]} for player '
                f'{voodooTeam["PLAYER NAME"][i]}')
            with open('./VoodooRoster.json', 'w') as f:
                f.write(json.dumps(voodooTeam))
            return

    await interaction.response.send_message('Player or stat does not exist')


@tree.command(name='increment-stats', description='Increment a players stats', guild=GUILD_ID)
async def incrementStats(interaction: discord.Interaction, member: discord.Member, goals: int = 0, assists: int = 0, pims: int = 0):
    memberID = member.id
    for i, ID in enumerate(voodooTeam['DISCORD USER ID']):
        if memberID == ID:
            voodooTeam['goals'.upper()][i] = voodooTeam['goals'.upper()
                                                        ][i] + goals
            voodooTeam['assists'.upper(
            )][i] = voodooTeam['assists'.upper()][i] + assists
            voodooTeam['pims'.upper()][i] = voodooTeam['pims'.upper()
                                                       ][i] + pims
            voodooTeam['points'.upper()][i] = voodooTeam['points'.upper(
            )][i] + voodooTeam['goals'.upper()][i] + voodooTeam['assists'.upper()][i]
            voodooTeam['ppg'.upper()][i] = voodooTeam['points'.upper()
                                                      ][i]/voodooTeam['gp'.upper()][i]
            await interaction.response.send_message(f'Incremented {voodooTeam["PLAYER NAME"][i]}\'s stats.')
            with open('./VoodooRoster.json', 'w') as f:
                f.write(json.dumps(voodooTeam))
            return

    await interaction.response.send_message('Player ID does not exist.')


# sheets test

# # Specify Google Sheet ID and range
# SHEET_ID = rosterSheet_id
# RANGE_NAME = 'Roster DB!A2:Z100'


# # Connect to Google Sheets API
# service = build('sheets', 'v4', credentials=creds)
# sheet = service.spreadsheets()


@tree.command(name='add-player-sheets', description='Adds a Player to the sheets db', guild=GUILD_ID)
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
    existing_players = sheet.values().get(
        spreadsheetId=ROSTER_SHEET_ID, range=ROSTER_DB_RANGE_NAME).execute().get('values', [])
    existing_ids = [row[2] for row in existing_players if len(row) > 2]
    if memberID in existing_ids:
        await interaction.response.send_message('Player with that discord ID already exists.')
        return

    # Append new player to roster
    new_player = [number, firstName, lastName, position, memberID, status, isCaptain, handedness,
                  gp, goals, assists, goals+assists, (goals+assists)/gp if gp != 0 else 0, pims]
    sheet.values().append(spreadsheetId=ROSTER_SHEET_ID, range=ROSTER_DB_RANGE_NAME, body={
        'values': [new_player]}, valueInputOption='RAW').execute()

    await interaction.response.send_message('Player added successfully.')
