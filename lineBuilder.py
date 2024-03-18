from discordStuff import *

@hockeyBot.event
async def on_message(message):

# if message is from sesh (aka event created)...
    if message.content and str(message.author) == 'sesh#1244':
        if int(re.search(r'\d+', str(message.content)).group(0)) == 1218300771318370395: # what's this id?
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

            # for player in flattenedPlayers:
            #     for i, databasePlayer in enumerate(voodooTeam['PLAYER NAME']):
            #         if player == databasePlayer:
            #             voodooTeam['GP'][i] += 1

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
