from services.discordStuff import *
import re
from services.sheets import *
import time
from datetime import datetime, timedelta
import services.cellOperations as cellOperations


@hockeyBot.event
async def on_message(message):
    if message.content and str(message.author) == 'sesh#1244':
        if int(re.search(r'\d+', str(message.content)).group(0)) == 1218300771318370395:
            RSVP_sheet_values = cellOperations.Get_Cell_Range(RSVP_SHEET_RANGE)

            excludedKeywords = ['Robot Database', 'Confirmed', 'Maybes']

            for j, row in enumerate(RSVP_sheet_values):
                if row and row[0] not in excludedKeywords:
                    row.pop(0)

            ranges_to_clear = ['RSVP Sheet!A2:H2', 'RSVP Sheet!A4:H19', 'RSVP Sheet!A21:H35']

            await cellOperations.Range_Clear(ranges_to_clear)
            await cellOperations.Update_Cell_Range(RSVP_SHEET_RANGE, RSVP_sheet_values)


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

    if after.content and str(after.author) == 'sesh#1244':
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

        RSVP_sheet_values = cellOperations.Get_Cell_Range(RSVP_SHEET_RANGE)

        existing_players = cellOperations.get_players()

        existing_IDs = []

        for player in existing_players:
            if len(player) >= 5:
                existing_IDs.append(player[4])

        Current_Scheduled_Games = RSVP_sheet_values[0]

        if not Current_Scheduled_Games:
            j = -1

        for j, gameTime in enumerate(Current_Scheduled_Games):
            if legibleDateTime == gameTime:
                colLetter = column_index_to_letter(j+1)

                Confirmed_Range = 'RSVP Sheet!'+colLetter+'4:'+colLetter+'19'
                Maybe_Range = 'RSVP Sheet!'+colLetter+'21:'+colLetter+'35'

                ranges_to_clear = [Confirmed_Range, Maybe_Range]

                await cellOperations.Range_Clear(ranges_to_clear)

                [confirmedPlayers, maybePlayers] = getPlayers(embedded_data)

                for i, id in enumerate(confirmedPlayers):
                    if id in existing_IDs:
                        index = existing_IDs.index(id)
                        First_Name = existing_players[index][1]
                        Position = existing_players[index][3]
                        Player_Cell = 'RSVP SHEET!' + colLetter + str(i + 4)
                        Player_Value = First_Name + ' (' + Position + ')'

                        await cellOperations.Update_Cell(Player_Cell, Player_Value)

                for i, id in enumerate(maybePlayers):
                    if id in existing_IDs:
                        index = existing_IDs.index(id)
                        First_Name = existing_players[index][1]
                        Position = existing_players[index][3]
                        Player_Cell = 'RSVP SHEET!' + colLetter + str(i + 21)
                        Player_Value = First_Name + ' (' + Position + ')'

                        await cellOperations.Update_Cell(Player_Cell, Player_Value)
                return

        colLetter = column_index_to_letter(j+2)

        Confirmed_Range = 'RSVP Sheet!' + colLetter + '4:' + colLetter + '19'
        Maybe_Range = 'RSVP Sheet!' + colLetter + '21:' + colLetter + '35'

        Date_Cell = 'RSVP SHEET!' + colLetter + '2'

        await cellOperations.Update_Cell(Date_Cell, legibleDateTime)

        ranges_to_clear = [Confirmed_Range, Maybe_Range]

        await cellOperations.Range_Clear(ranges_to_clear)

        [confirmedPlayers, maybePlayers] = getPlayers(embedded_data)

        for i, id in enumerate(confirmedPlayers):
            if id in existing_IDs:
                index = existing_IDs.index(id)
                First_Name = existing_players[index][1]
                Position = existing_players[index][3]
                Player_Cell = 'RSVP SHEET!' + colLetter + str(i + 4)
                Player_Value = First_Name + ' (' + Position + ')'

                await cellOperations.Update_Cell(Player_Cell, Player_Value)

        for i, id in enumerate(maybePlayers):
            if id in existing_IDs:
                index = existing_IDs.index(id)
                First_Name = existing_players[index][1]
                Position = existing_players[index][3]
                Player_Cell = 'RSVP SHEET!' + colLetter + str(i + 21)
                Player_Value = First_Name + ' (' + Position + ')'

                await cellOperations.Update_Cell(Player_Cell, Player_Value)
