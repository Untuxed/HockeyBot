import cv2
from datetime import datetime, timedelta
from utils.genericFunctions import get_game_date, get_roster, get_season_and_game_id
import services.cellOperations as cellOperations
import services.sheets as sheets
import random
from services.firebaseStuff import *
import cairosvg
import re


async def imageGenerator(interaction):
    def rosterLookup(playerName, roster):
        if playerName:
            for i, playerData in enumerate(roster):
                name_parts = playerData.replace('[', '').replace(']', '').split(' ')
                _, _, number = name_parts[:3]
                if playerName in playerData:
                    return f'{number} - ' + playerName
            return '## - ' + playerName
        else:
            return ' '

    def randomTextColor():
        return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)

    def addGameInfo(baseSVGFile, newImageFilePath, opponentName, gameTime, gameDate):
        temp_SVG_FilePath = './resources/images/temp.svg'

        gameDate = gameDate.strftime('%m-%d')

        SVG_Game_Info = baseSVGFile.replace('### REPLACE ME ###',
                                            opponentName[3:-2] + ': ' + gameDate + ', ' + gameTime)

        with open(temp_SVG_FilePath, 'w') as file:
            file.write(SVG_Game_Info)

        cairosvg.svg2png(url=temp_SVG_FilePath, write_to=newImageFilePath)

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

    def writeTempFiles(desc, custom=''):
        image_blob_name = f'LineupImages/{custom}lineupWithName_{game_id}.png'
        description = desc
        image_firebase_database_reference = db.collection(season_id).document('games').collection(game_id).document('Lineup_Cards')
        filename = f'./resources/images/temp_{custom}BaseLineupCard.png'
        blob = bucket.blob(image_blob_name)
        blob.upload_from_filename(filename)
        url = blob.generate_signed_url(expiration=timedelta(days=31))

        lineup_doc = db.collection(season_id).document('games').collection(game_id).document('Lineup_Cards').get()

        if not lineup_doc.exists:
            image_firebase_database_reference.set({
                f'{custom}image_url': image_blob_name,
                f'{custom}description': description,
                f'{custom}signed_url': url
            })
        else:
            image_firebase_database_reference.update({
                f'{custom}image_url': image_blob_name,
                f'{custom}description': description,
                f'{custom}signed_url': url
            })
        return

    await interaction.response.defer()
    next_game_date, next_game_time, opponent = get_game_date(interaction)

    Base_Lineup_Image_Path = 'LineupImages/BaseLineupCard.svg'
    Dennis_Base_Lineup_Image_Path = 'LineupImages/Dennis_BaseLineupCard.svg'

    Base_Lineup_Image = bucket.blob(Base_Lineup_Image_Path).download_as_text()
    Dennis_Base_Lineup_Image = bucket.blob(Dennis_Base_Lineup_Image_Path).download_as_text()

    if next_game_time and next_game_date:
        addGameInfo(Base_Lineup_Image,
                    './resources/images/temp_BaseLineupCard.png',
                    opponent,
                    next_game_time,
                    next_game_date
                    )

        addGameInfo(Dennis_Base_Lineup_Image,
                    './resources/images/temp_Dennis_BaseLineupCard.png',
                    opponent,
                    next_game_time,
                    next_game_date
                    )
    else:
        return

    rosteredSkaters, rosteredGoalies = get_roster(interaction)

    Forwards = [
        [
            name.split()[0] if name else '' for name in sublist
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

    Base_Lineup_Image = cv2.imread('./resources/images/temp_BaseLineupCard.png')
    Dennis_Base_Lineup_Image = cv2.imread('./resources/images/temp_Dennis_BaseLineupCard.png')

    for Line_Number, Line in enumerate(Forwards):
        LW_Text = rosterLookup(Line[0], rosteredSkaters)
        C_Text = rosterLookup(Line[1], rosteredSkaters)
        RW_Text = rosterLookup(Line[2], rosteredSkaters)

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
        LD_Text = rosterLookup(Line[0], rosteredSkaters)
        RD_Text = rosterLookup(Line[1], rosteredSkaters)

        _ = addPlayerLineup(Base_Lineup_Image, LD_Text, 947.5, 870 + Line_Number * Defense_Y_Spacing)
        _ = addPlayerLineup(Base_Lineup_Image, RD_Text, 1611.25, 870 + Line_Number * Defense_Y_Spacing)

        _ = addPlayerLineup(Dennis_Base_Lineup_Image, LD_Text, 947.5, 870 + Line_Number * Forward_Y_Spacing,
                            randomTextColor())
        _ = addPlayerLineup(Dennis_Base_Lineup_Image, RD_Text, 1611.25, 870 + Line_Number * Forward_Y_Spacing,
                            randomTextColor())

    G_Text = rosterLookup(Goalie[0][1], rosteredGoalies)

    Lineup_Image_W_Text = addPlayerLineup(Base_Lineup_Image, G_Text, 1327.5, 1500)
    Dennis_Lineup_Image_W_Text = addPlayerLineup(Dennis_Base_Lineup_Image, G_Text, 1327.5, 1500,
                                                 randomTextColor())

    category_name = interaction.channel.category.name  # season_id gets created from category name in discord
    season_id = re.sub(r'\s+', '_', category_name).lower()

    if next_game_date:
        game_id = next_game_date.strftime('%m-%d-%Y')

        cv2.imwrite(f'./resources/images/temp_BaseLineupCard.png', Lineup_Image_W_Text)
        cv2.imwrite(f'./resources/images/temp_Dennis_BaseLineupCard.png', Dennis_Lineup_Image_W_Text)

        writeTempFiles(desc='Basic Lineup Card')
        writeTempFiles(desc='Dennis Lineup Card', custom='Dennis_')

        return True
    else:
        return False


def pullImage(interaction):
    next_game_date, _, _ = get_game_date(interaction)
    if next_game_date is None:
        return None, None
    game_id = next_game_date.strftime('%m-%d-%Y')

    category_name = interaction.channel.category.name
    season_id = re.sub(r'\s+', '_', category_name).lower()

    lineup_card_dict = db.collection(season_id).document('games').collection(game_id).document('Lineup_Cards').get().to_dict()

    if next_game_date:
        if 'messageID' in lineup_card_dict:
            return lineup_card_dict['signed_url'], lineup_card_dict['Dennis_image_url'], lineup_card_dict['messageID']
        else:
            return lineup_card_dict['signed_url'], lineup_card_dict['Dennis_image_url'], None
    else:
        return
    