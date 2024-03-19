from discordStuff import *
import re
from sheets import *
import time
from datetime import datetime, timedelta


@hockeyBot.event
async def on_message(message):
    if message.content and str(message.author) == 'sesh#1244':
        if int(re.search(r'\d+', str(message.content)).group(0)) == 1218300771318370395:
            RSVP_sheet_values = SHEET.values().get(
                spreadsheetId=VOODOO_SHEET_ID,
                range=RSVP_SHEET_RANGE,
                valueRenderOption='FORMATTED_VALUE').execute().get('values', [])

            excludedKeywords = ['Robot Database', 'Confirmed', 'Maybes']

            # forwardsRange = 'A3:C6'
            # defenseRange = 'A9:C12'
            # goalieRange = 'A14:C14'
            #
            # players = [
            #     name for sublist in
            #     [
            #         sheet.get(forwardsRange),
            #         sheet.get(defenseRange),
            #         sheet.get(goalieRange)
            #     ] for inner_list in sublist for name in inner_list
            # ]
            # flattenedPlayers = [name for name in players if name != '']
            #
            # Database_Players = sheet.values().get(spreadsheetId=VOODOO_SHEET_ID,
            #                              range=ROSTER_DB_RANGE_NAME).execute().get('values', [])
            #
            # for player in flattenedPlayers:
            #     for i, Database_Player in Database_Players:
            #         if player == Database_Player[1] or player == Database_Player[2]:
            #             # Update the player's stats
            #             Database_Player[8] = int(Database_Player[8] + 1)  # Update GP
            #
            #             # Update the player's stats in the Google Sheet
            #             sheet.values().update(
            #                 spreadsheetId=VOODOO_SHEET_ID,
            #                 range=f'ROSTER DB!A{i + 2}:N{i + 2}',
            #                 valueInputOption='USER_ENTERED',
            #                 body={'values': [player]}
            #             ).execute()
            #             print('increment GP')
            #             return

            for j, row in enumerate(RSVP_sheet_values):
                if row and row[0] not in excludedKeywords:
                    row.pop(0)

            ranges_to_clear = ['RSVP Sheet!A2:H2', 'RSVP Sheet!A4:H19', 'RSVP Sheet!A21:H35']
            for range in ranges_to_clear:
                SHEET.values().clear(spreadsheetId=VOODOO_SHEET_ID, range=range).execute()

            SHEET.values().update(
                spreadsheetId=VOODOO_SHEET_ID,
                range=RSVP_SHEET_RANGE,
                valueInputOption='RAW',
                body={"values": RSVP_sheet_values}
            ).execute()


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

                existing_players = SHEET.values().get(
                    spreadsheetId=VOODOO_SHEET_ID, range=ROSTER_DB_RANGE_NAME).execute().get('values', [])
                existing_ids = [row[4] for row in existing_players if len(row) > 2]

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
