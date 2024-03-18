# TODO: Fix usage with polls
# TODO: change getworksheet to be by name
import json
import os
import re
from tabulate import tabulate
from datetime import datetime, timedelta
import time
from googleStuff import *
from discordStuff import *
from sheets import *

if os.path.isfile('./VoodooRoster.json'):
    with open('./VoodooRoster.json') as f:
        voodooTeam = json.loads(f.read())
else:
    voodooTeam = {
        'PLAYER NAME': [],
        'POSITION': [],
        'DISCORD USER ID': [],
        'STATUS': [],
        'IS_CAPTAIN': [],
        'HANDEDNESS': [],
        'NUMBER': [],
        'GP': [],
        'GOALS': [],
        'ASSISTS': [],
        'POINTS': [],
        'PPG': [],
        'PIMS': []
    }


@hockeyBot.event
async def on_ready():
    print(f'{hockeyBot.user.name} has connected to Discord!')
    await tree.sync(guild=GUILD_ID)


@hockeyBot.event
async def on_message(message):
    if str(message.author) == 'HockeyBot#3547':
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

    if message.content.startswith('$lines'):
        await message.add_reaction("🤩")

    if message.content and str(message.author) == 'sesh#1244':
        if int(re.search(r'\d+', str(message.content)).group(0)) == 1218300771318370395:
            botSheetValues = botSheet.get_all_values()
            excludedKeywords = ['Robot Database', 'Confirmed', 'Maybes']

            forwardsRange = 'A3:C6'
            defenseRange = 'A9:C12'
            goalieRange = 'A14:C14'

            players = [
                name for sublist in
                [
                    sheet.get(forwardsRange),
                    sheet.get(defenseRange),
                    sheet.get(goalieRange)
                ] for inner_list in sublist for name in inner_list
            ]
            flattenedPlayers = [name for name in players if name != '']

            for player in flattenedPlayers:
                for i, databasePlayer in enumerate(voodooTeam['PLAYER NAME']):
                    if player == databasePlayer:
                        voodooTeam['GP'][i] += 1

            for row in botSheetValues:
                if row[0] not in excludedKeywords:
                    row.pop(0)

            botSheet.update(botSheetValues)


@hockeyBot.event
async def on_message_edit(_, after):
    def column_index_to_letter(numericalIndex):
        dividend = numericalIndex
        column_letter = ''
        while dividend > 0:
            modulo = (dividend - 1) % 26
            column_letter = chr(65 + modulo) + column_letter
            dividend = (dividend - modulo) // 26
        return column_letter

    def getPlayers(data):
        confirmed = data.fields[1].value
        maybes = data.fields[2].value

        return [re.findall(r'\d+', str(confirmed)), re.findall(r'\d+', str(maybes))]

    if after.content:
        if int(re.search(r'\d+', str(after.content)).group(0)) == 1218300771318370395:
            return

    if str(after.author) == 'sesh#1244':
        embedded_data = after.embeds[0]
        gameTime = int(
            re.search(r'\d+', str(embedded_data.fields[0].value)).group())
        if gameTime - 10 < int(time.time()):
            return
        legibleDateTime = str(datetime.utcfromtimestamp(
            gameTime) - timedelta(hours=4))
        currentScheduledGames = botSheet.row_values(2)

        if not currentScheduledGames:
            j = -1

        for j, gameTime in enumerate(currentScheduledGames):
            if legibleDateTime == gameTime:
                colLetter = column_index_to_letter(j+1)

                confirmedSheetRange = [colLetter+'4:'+colLetter+'19']
                botSheet.batch_clear(confirmedSheetRange)

                maybeSheetRange = [colLetter+'21:'+colLetter+'26']
                botSheet.batch_clear(maybeSheetRange)

                [confirmedPlayers, maybePlayers] = getPlayers(embedded_data)

                for i, id in enumerate(confirmedPlayers):
                    index = voodooTeam["DISCORD USER ID"].index(int(id))
                    position = voodooTeam["POSITION"][index]
                    botSheet.update_cell(
                        i+4, j+1, voodooTeam["PLAYER NAME"][index] + ' (' + position + ')')
                for i, id in enumerate(maybePlayers):
                    index = voodooTeam["DISCORD USER ID"].index(int(id))
                    position = voodooTeam["POSITION"][index]
                    botSheet.update_cell(
                        i+21, j+1, voodooTeam["PLAYER NAME"][index] + ' (' + position + ')')
                return

        colLetter = column_index_to_letter(j+2)
        botSheet.update_cell(2, j+2, legibleDateTime)

        confirmedSheetRange = [colLetter + '4:' + colLetter + '19']
        botSheet.batch_clear(confirmedSheetRange)

        maybeSheetRange = [colLetter + '21:' + colLetter + '26']
        botSheet.batch_clear(maybeSheetRange)

        [confirmedPlayers, maybePlayers] = getPlayers(embedded_data)

        for i, id in enumerate(confirmedPlayers):
            index = voodooTeam["DISCORD USER ID"].index(int(id))
            position = voodooTeam["POSITION"][index]
            botSheet.update_cell(
                i + 4, j + 2, voodooTeam["PLAYER NAME"][index] + ' (' + position + ')')

        for i, id in enumerate(maybePlayers):
            index = voodooTeam["DISCORD USER ID"].index(int(id))
            position = voodooTeam["POSITION"][index]
            botSheet.update_cell(
                i + 21, j + 2, voodooTeam["PLAYER NAME"][index] + ' (' + position + ')')


@hockeyBot.event
async def on_scheduled_event_create(event):
    if event:
        hockeyBot.get_channel()


@hockeyBot.event
async def on_scheduled_event_user_add(event, user):
    if user:
        print(user)


@tree.command(name='get-events', description='Test', guild=GUILD_ID)
async def getChannels(interaction: discord.Interaction):
    subbedUsers = hockeyBot.guilds[1].scheduled_events[0].users(
        limit=20, oldest_first=True)
    players = []

    async for u in subbedUsers:
        players.append(u.id)

    await interaction.response.send_message(players)


@tree.command(name="avatar", description="Get user avatar", guild=GUILD_ID)
async def avatar(interaction: discord.Interaction, member: discord.Member):
    await interaction.response.send_message(member.display_avatar)


@tree.command(name='add-player', description='Adds a Player to the roster', guild=GUILD_ID)
async def addPlayer(interaction: discord.Interaction, member: discord.Member, gp: int = 0, goals: int = 0, assists: int = 0, pims: int = 0):
    memberID = member.id
    memberRoles = member.roles

    position = 'not-specified'
    status = 'friend-of-the-program'
    isCaptain = False
    handedness = 'not-specified'

    number = re.search(r'\[(\d+)\]', str(member.display_name))
    name = str(member.display_name).split()[0]

    if not name:
        name = 'nameless'

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

    for i in voodooTeam['DISCORD USER ID']:
        if memberID == i and len(voodooTeam) > 0:
            await interaction.response.send_message('Player with that discord ID already exists.')
            return

    voodooTeam['PLAYER NAME'].append(name)
    voodooTeam['POSITION'].append(position)
    voodooTeam['DISCORD USER ID'].append(memberID)
    voodooTeam['STATUS'].append(status)
    voodooTeam['IS_CAPTAIN'].append(isCaptain)
    voodooTeam['HANDEDNESS'].append(handedness)
    voodooTeam['NUMBER'].append(number)
    voodooTeam['GP'].append(gp)
    voodooTeam['GOALS'].append(goals)
    voodooTeam['ASSISTS'].append(assists)
    voodooTeam['POINTS'].append(goals+assists)
    voodooTeam['PPG'].append((goals+assists)/gp)
    voodooTeam['PIMS'].append(pims)

    with open('./VoodooRoster.json', 'w') as f:
        f.write(json.dumps(voodooTeam))

    await interaction.response.send_message(voodooTeam)


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


@tree.command(name='view-all-stats', description='Views all stats for a player', guild=GUILD_ID)
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

# token
hockeyBot.run(
    '')
