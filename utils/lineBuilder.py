# from services.discordStuff import *
# import re
# import time
# from datetime import datetime, timedelta
# from services.cellOperations import *


# @hockeyBot.event
# async def on_message(message):
#     if message.content and str(message.author) == 'sesh#1244':
#         if int(re.search(r'\d+', str(message.content)).group(0)) == 1218300771318370395:
#             RSVP_sheet_values = Get_Cell_Range(RSVP_SHEET_RANGE)

#             excludedKeywords = ['Robot Database', 'Confirmed', 'Maybes', 'Scratches']

#             for j, row in enumerate(RSVP_sheet_values):
#                 if row and row[0] not in excludedKeywords:
#                     row.pop(0)

#             RSVP_Dates_Range = 'RSVP Sheet!A2:H2'
#             RSVP_Confirmed_Range = 'RSVP Sheet!A4:H19'
#             RSVP_Maybe_Range = 'RSVP Sheet!A21:H35'
#             RSVP_Scratch_Range = 'RSVP Sheet!A37:H50'

#             ranges_to_clear = [RSVP_Dates_Range, RSVP_Confirmed_Range, RSVP_Maybe_Range, RSVP_Scratch_Range]

#             await Range_Clear(ranges_to_clear)
#             await Update_Cell_Range(RSVP_SHEET_RANGE, RSVP_sheet_values)


# @hockeyBot.event
# async def on_message_edit(_, after):
#     def column_index_to_letter(numericalIndex):
#         dividend = numericalIndex
#         column_letter = ''
#         while dividend > 0:
#             modulo = (dividend - 1) % 26
#             column_letter = chr(65 + modulo) + column_letter
#             dividend = (dividend - modulo) // 26
#         return column_letter

#     def getPlayers(data):
#         confirmed = data.fields[1].value
#         maybes = data.fields[2].value
#         scratches = data.fields[3].value

#         return [re.findall(r'\d+', str(confirmed)), re.findall(r'\d+', str(maybes)), re.findall(r'\d+', str(scratches))]

#     if after.content and str(after.author) == 'sesh#1244':
#         if int(re.search(r'\d+', str(after.content)).group(0)) == 1218300771318370395:
#             return

#     if str(after.author) == 'sesh#1244':
#         embedded_data = after.embeds[0]
#         gameTime = int(
#             re.search(r'\d+', str(embedded_data.fields[0].value)).group())
#         if gameTime - 10 < int(time.time()):
#             return
#         legibleDateTime = str(datetime.utcfromtimestamp(
#             gameTime) - timedelta(hours=4))

#         RSVP_sheet_values = Get_Cell_Range(RSVP_SHEET_RANGE)

#         existing_players = get_players()

#         existing_IDs = []

#         for player in existing_players:
#             if len(player) >= 5:
#                 existing_IDs.append(player[4])

#         Current_Scheduled_Games = RSVP_sheet_values[0]

#         if not Current_Scheduled_Games:
#             j = -1

#         for j, gameTime in enumerate(Current_Scheduled_Games):
#             if legibleDateTime == gameTime:
#                 colLetter = column_index_to_letter(j + 1)

#                 Confirmed_Range = 'RSVP Sheet!' + colLetter + '4:' + colLetter + '19'
#                 Maybe_Range = 'RSVP Sheet!' + colLetter + '21:' + colLetter + '35'
#                 Scratch_Range = 'RSVP Sheet!' + colLetter + '37:' + colLetter + '50'

#                 ranges_to_clear = [Confirmed_Range, Maybe_Range, Scratch_Range]

#                 await Range_Clear(ranges_to_clear)

#                 [confirmedPlayers, maybePlayers, scratchedPlayers] = getPlayers(embedded_data)

#                 Confirmed_Player_Values = []
#                 Confirmed_Player_Range = 'RSVP Sheet!' + colLetter + '4:' + colLetter + str(4 + len(confirmedPlayers))

#                 Maybe_Player_Values = []
#                 Maybe_Player_Range = 'RSVP Sheet!' + colLetter + '21:' + colLetter + str(len(21 + maybePlayers))

#                 Scratched_Player_Values = []
#                 Scratched_Player_Range = 'RSVP Sheet!' + colLetter + '37:' + colLetter + str(len(37 + maybePlayers))

#                 for i, id in enumerate(confirmedPlayers):
#                     if id in existing_IDs:
#                         index = existing_IDs.index(id)
#                         First_Name = existing_players[index][1]
#                         Position = existing_players[index][3]
#                         Confirmed_Player_Values.append(First_Name + ' (' + Position + ')')

#                 for i, id in enumerate(maybePlayers):
#                     if id in existing_IDs:
#                         index = existing_IDs.index(id)
#                         First_Name = existing_players[index][1]
#                         Position = existing_players[index][3]
#                         Maybe_Player_Values.append(First_Name + ' (' + Position + ')')

#                 for i, id in enumerate(scratchedPlayers):
#                     if id in existing_IDs:
#                         index = existing_IDs.index(id)
#                         First_Name = existing_players[index][1]
#                         Position = existing_players[index][3]
#                         Scratched_Player_Values.append(First_Name + ' (' + Position + ')')

#                 await Update_Cell_Range(Confirmed_Player_Range, Confirmed_Player_Values)
#                 await Update_Cell_Range(Maybe_Player_Range, Maybe_Player_Values)
#                 await Update_Cell_Range(Scratched_Player_Range, Scratched_Player_Values)
#                 return

#         colLetter = column_index_to_letter(j + 2)

#         Confirmed_Range = 'RSVP Sheet!' + colLetter + '4:' + colLetter + '19'
#         Maybe_Range = 'RSVP Sheet!' + colLetter + '21:' + colLetter + '35'
#         Scratch_Range = 'RSVP Sheet!' + colLetter + '37:' + colLetter + '50'

#         Date_Cell = 'RSVP SHEET!' + colLetter + '2'

#         await Update_Cell(Date_Cell, legibleDateTime)

#         ranges_to_clear = [Confirmed_Range, Maybe_Range, Scratch_Range]

#         await Range_Clear(ranges_to_clear)

#         [confirmedPlayers, maybePlayers, scratchedPlayers] = getPlayers(embedded_data)

#         Confirmed_Player_Values = []
#         Confirmed_Player_Range = 'RSVP Sheet!' + colLetter + '4:' + colLetter + str(4 + len(confirmedPlayers))

#         Maybe_Player_Values = []
#         Maybe_Player_Range = 'RSVP Sheet!' + colLetter + '21:' + colLetter + str(len(21 + maybePlayers))

#         Scratched_Player_Values = []
#         Scratched_Player_Range = 'RSVP Sheet!' + colLetter + '37:' + colLetter + str(len(37 + maybePlayers))

#         for i, id in enumerate(confirmedPlayers):
#             if id in existing_IDs:
#                 index = existing_IDs.index(id)
#                 First_Name = existing_players[index][1]
#                 Position = existing_players[index][3]
#                 Confirmed_Player_Values.append(First_Name + ' (' + Position + ')')

#         for i, id in enumerate(maybePlayers):
#             if id in existing_IDs:
#                 index = existing_IDs.index(id)
#                 First_Name = existing_players[index][1]
#                 Position = existing_players[index][3]
#                 Maybe_Player_Values.append(First_Name + ' (' + Position + ')')

#         for i, id in enumerate(scratchedPlayers):
#             if id in existing_IDs:
#                 index = existing_IDs.index(id)
#                 First_Name = existing_players[index][1]
#                 Position = existing_players[index][3]
#                 Scratched_Player_Values.append(First_Name + ' (' + Position + ')')

#         await Update_Cell_Range(Confirmed_Player_Range, Confirmed_Player_Values)
#         await Update_Cell_Range(Maybe_Player_Range, Maybe_Player_Values)
#         await Update_Cell_Range(Scratched_Player_Range, Scratched_Player_Values)
#         return
