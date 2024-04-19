import cv2
from datetime import datetime
from utils.genericFunctions import get_game_date
import services.cellOperations as cellOperations
import services.sheets as sheets
import random
from services.firebaseStuff import *
# import cairosvg


def imageGenerator(interaction):
    def numberLookup(playerName):
        if playerName:
            if playerName in existing_names:
                index = existing_names.index(playerName)
                Player_Number = existing_players[index][0]
                return f'{Player_Number} - ' + playerName
            else:
                return '## - ' + playerName
        else:
            return ' '

    def randomTextColor():
        return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)

    def addGameInfo(baseSVGFilePath, newImageFilePath, opponentName, gameTime):
        temp_SVG_FilePath = './../resources/images/temp.svg'

        with open(baseSVGFilePath, 'r') as file:
            base_SVG_Data = file.read()

        SVG_Game_Info = base_SVG_Data.replace('### REPLACE ME ###', opponentName + gameTime)

        with open(temp_SVG_FilePath, 'w') as file:
            file.write(SVG_Game_Info)

        # cairosvg.svg2png(url=temp_SVG_FilePath, write_to=newImageFilePath)

    def addPlayerLineup(baseImage, playerText, x_anchor, y_location, Font_Color=(0, 0, 0)):
        Font_Size = 1.5
        Font_Weight = 3
        Font_Type = cv2.FONT_HERSHEY_DUPLEX

        text_Width = cv2.getTextSize(playerText, Font_Type, fontScale=Font_Size, thickness=Font_Weight)
        return cv2.putText(
            baseImage,
            playerText,
            (int(x_anchor - (text_Width[0][0] / 2)), y_location),
            fontFace=Font_Type,
            fontScale=Font_Size,
            color=Font_Color,
            thickness=Font_Weight
        )

    next_game_date, next_game_time, opponent = get_game_date(interaction)
    Game_Dates = cellOperations.Get_Cell_Range(sheets.RSVP_SHEET_RANGE)[0]
    Earliest_Game_Date = Game_Dates[0]

    if Earliest_Game_Date:
        addGameInfo('./../resources/images/BaseLineupCard.svg',
                    './../resources/images/BaseLineupCard.png',
                    'OpponentName',
                    datetime.strptime(Earliest_Game_Date, '%H:%M')
                    )

        addGameInfo('./../resources/images/Dennis_BaseLineupCard.svg',
                    './../resources/images/Dennis_BaseLineupCard.png',
                    'OpponentName',
                    datetime.strptime(Earliest_Game_Date, '%H:%M')
                    )
    else:
        return

    Earliest_Game_Date = datetime.strptime(Earliest_Game_Date, '%Y-%m-%d %H:%M:%S')

    Base_Lineup_Image_Path = 'LineupImages/BaseLineupCard.svg'
    Dennis_Base_Lineup_Image_Path = 'LineupImages/Dennis_BaseLineupCard.svg'

    Base_Lineup_Image = bucket.blob(Base_Lineup_Image_Path).download_as_text()
    Dennis_Base_Lineup_Image = bucket.blob(Dennis_Base_Lineup_Image_Path).download_as_text()

    existing_players = cellOperations.get_players()

    existing_names = []

    for player in existing_players:
        if len(player) >= 5:
            existing_names.append(player[1])

    Forwards = [
        [
            name.split()[0] for name in sublist
        ] for sublist in cellOperations.Get_Cell_Range(sheets.FORWARDS_LINEUP_RANGE)]

    if not Forwards:
        Forwards = [
            ['Player #1', 'Player #2', 'Player #3'],
            ['Player #4', 'Player #5', 'Player #6'],
            ['Player #7', 'Player #8', 'Player #9'],
            ['Player #10', 'Player #11', 'Player #12']
        ]

    Defense = [
        [
            item for item in sublist if item.strip()
        ] for sublist in cellOperations.Get_Cell_Range(sheets.DEFENSE_LINEUP_RANGE)]
    Defense = [[name.split()[0] for name in sublist] for sublist in Defense]

    if not Defense:
        Defense = [
            ['Player #1', 'Player #2'],
            ['Player #3', 'Player #4'],
            ['Player #5', 'Player #6']
        ]

    Goalie = [
        [
            name.split()[0] if name else '' for name in sublist
        ] for sublist in cellOperations.Get_Cell_Range(sheets.GOALIE_LINEUP_RANGE)]

    if not Goalie:
        Goalie = [[' ', 'Goalie #1', ' ']]

    Forward_Y_Spacing = int(515 / len(Forwards))
    Defense_Y_Spacing = int(500 / len(Defense))

    for Line_Number, Line in enumerate(Forwards):
        LW_Text = numberLookup(Line[0])
        C_Text = numberLookup(Line[1])
        RW_Text = numberLookup(Line[2])

        _ = addPlayerLineup(Base_Lineup_Image, LW_Text, 947.5, 200 + Line_Number * Forward_Y_Spacing)
        _ = addPlayerLineup(Base_Lineup_Image, C_Text, 1327.5, 200 + Line_Number * Forward_Y_Spacing)
        _ = addPlayerLineup(Base_Lineup_Image, RW_Text, 1702.5, 200 + Line_Number * Forward_Y_Spacing)

        _ = addPlayerLineup(Dennis_Base_Lineup_Image, LW_Text, 947.5, 200 + Line_Number * Forward_Y_Spacing,
                            randomTextColor())
        _ = addPlayerLineup(Dennis_Base_Lineup_Image, C_Text, 1327.5, 200 + Line_Number * Forward_Y_Spacing,
                            randomTextColor())
        _ = addPlayerLineup(Dennis_Base_Lineup_Image, RW_Text, 1702.5, 200 + Line_Number * Forward_Y_Spacing,
                            randomTextColor())

    for Line_Number, Line in enumerate(Defense):
        LD_Text = numberLookup(Line[0])
        RD_Text = numberLookup(Line[1])

        _ = addPlayerLineup(Base_Lineup_Image, LD_Text, 380, 870 + Line_Number * Defense_Y_Spacing)
        _ = addPlayerLineup(Base_Lineup_Image, RD_Text, 1611.25, 870 + Line_Number * Defense_Y_Spacing)

        _ = addPlayerLineup(Dennis_Base_Lineup_Image, LD_Text, 947.5, 200 + Line_Number * Forward_Y_Spacing,
                            randomTextColor())
        _ = addPlayerLineup(Dennis_Base_Lineup_Image, RD_Text, 947.5, 200 + Line_Number * Forward_Y_Spacing,
                            randomTextColor())

    G_Text = numberLookup(Goalie[0][1])

    Lineup_Image_W_Text = addPlayerLineup(Base_Lineup_Image, G_Text, 1327.5, 1500)
    Dennis_Lineup_Image_W_Text = addPlayerLineup(Base_Lineup_Image, G_Text, 1327.5, 1500,
                                                 randomTextColor())

    if Earliest_Game_Date:
        timestamp = (Earliest_Game_Date - datetime(1970, 1, 1)).total_seconds()
        cv2.imwrite(f'./../resources/images/LineUpWithName_{timestamp}.png', Lineup_Image_W_Text)
        cv2.imwrite(f'./../resources/images/DennisLineUpWithName_{timestamp}.png', Dennis_Lineup_Image_W_Text)
        return f'./../resources/images/LineUpWithName_{timestamp}.png'
    else:
        return


def pullImage():
    Game_Dates = cellOperations.Get_Cell_Range(sheets.RSVP_SHEET_RANGE)[0]
    Earliest_Game_Date = Game_Dates[0]

    Earliest_Game_Date = datetime.strptime(Earliest_Game_Date, '%Y-%m-%d %H:%M:%S')

    if Earliest_Game_Date:
        timestamp = (Earliest_Game_Date - datetime(1970, 1, 1)).total_seconds()
        return (f'./../resources/images/LineUpWithName_{timestamp}.png',
                f'./../resources/images/DennisLineUpWithName_{timestamp}.png')
    else:
        return
