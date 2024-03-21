import cv2
from datetime import datetime
import cellOperations
import sheets


# Forwards Pixel Range 860 x 200 to 1950 x 715

def imageGenerator():
    def numberLookup(playerName):
        if playerName:
            if playerName in existing_names:
                index = existing_names.index(playerName)
                Player_Number = existing_players[index][0]
                return f'{Player_Number} - ' + Line[0]
            else:
                return '## - ' + Line[0]
        else:
            return ' '

    Base_Lineup_Image = cv2.imread('./BaseLineupCard.png')

    Font_Size = 1.2
    Font_Weight = 2
    Font_Color = (0, 0, 0)
    Font_Type = cv2.FONT_HERSHEY_DUPLEX

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
            ['Player #1', 'Player #2', 'Player #3'],
            ['Player #1', 'Player #2', 'Player #3'],
            ['Player #1', 'Player #2', 'Player #3']
        ]

    Defense = [
        [
            item for item in sublist if item.strip()
        ] for sublist in cellOperations.Get_Cell_Range(sheets.DEFENSE_LINEUP_RANGE)]
    Defense = [[name.split()[0] for name in sublist] for sublist in Defense]

    if not Defense:
        Defense = [
            ['Player #1', 'Player #2'],
            ['Player #1', 'Player #2'],
            ['Player #1', 'Player #2']
        ]

    Goalie = [
        [
            name.split()[0] if name else '' for name in sublist
        ] for sublist in cellOperations.Get_Cell_Range(sheets.GOALIE_LINEUP_RANGE)]

    if not Goalie:
        Goalie = [[' ', 'Goalie #1', ' ']]

    Forward_Y_Spacing = int(515 / len(Forwards))
    Defense_Y_Spacing = int(500 / len(Defense))

    for i, Line in enumerate(Forwards):
        LW_Text = numberLookup(Line[0])
        C_Text = numberLookup(Line[1])
        RW_Text = numberLookup(Line[2])

        LW_Width = cv2.getTextSize(LW_Text, Font_Type, fontScale=Font_Size, thickness=Font_Weight)
        C_Width = cv2.getTextSize(C_Text, Font_Type, fontScale=Font_Size, thickness=Font_Weight)
        RW_Width = cv2.getTextSize(RW_Text, Font_Type, fontScale=Font_Size, thickness=Font_Weight)

        cv2.putText(
            Base_Lineup_Image,
            LW_Text,
            (int(760 + (375 - LW_Width[0][0]) / 2), 200 + i * Forward_Y_Spacing),
            fontFace=Font_Type,
            fontScale=Font_Size,
            color=Font_Color,
            thickness=Font_Weight
        )

        cv2.putText(
            Base_Lineup_Image,
            C_Text,
            (int(1327.5 - C_Width[0][0] / 2), 200 + i * Forward_Y_Spacing),
            fontFace=Font_Type,
            fontScale=Font_Size,
            color=Font_Color,
            thickness=Font_Weight
        )

        cv2.putText(
            Base_Lineup_Image,
            RW_Text,
            (int(1515 + (375 - RW_Width[0][0]) / 2), 200 + i * Forward_Y_Spacing),
            fontFace=Font_Type,
            fontScale=Font_Size,
            color=Font_Color,
            thickness=Font_Weight
        )

    for i, Line in enumerate(Defense):
        LD_Text = numberLookup(Line[0])
        RD_Text = numberLookup(Line[1])

        LD_Width = cv2.getTextSize(LD_Text, Font_Type, fontScale=Font_Size, thickness=Font_Weight)
        RD_Width = cv2.getTextSize(RD_Text, Font_Type, fontScale=Font_Size, thickness=Font_Weight)

        cv2.putText(
            Base_Lineup_Image,
            LD_Text,
            (int(760 + (567.5 - LD_Width[0][0]) / 2), 870 + i * Defense_Y_Spacing),
            fontFace=Font_Type,
            fontScale=Font_Size,
            color=Font_Color,
            thickness=Font_Weight
        )

        cv2.putText(
            Base_Lineup_Image,
            RD_Text,
            (int(1327.5 + (567.5 - RD_Width[0][0]) / 2), 870 + i * Defense_Y_Spacing),
            fontFace=Font_Type,
            fontScale=Font_Size,
            color=Font_Color,
            thickness=Font_Weight
        )

    G_Text = numberLookup(Goalie[0][1])

    Lineup_Image_W_Text = cv2.putText(
        Base_Lineup_Image,
        G_Text,
        (int(1327.5 - C_Width[0][0] / 2), 1500),
        fontFace=Font_Type,
        fontScale=Font_Size,
        color=Font_Color,
        thickness=Font_Weight
    )

    Game_Dates = cellOperations.Get_Cell_Range(sheets.RSVP_SHEET_RANGE)[0]
    Earliest_Game_Date = Game_Dates[0]

    if Earliest_Game_Date:
        timestamp = (Earliest_Game_Date - datetime(1970, 1, 1)).total_seconds()
        cv2.imwrite(f'./LineUpWithName_{timestamp}.png', Lineup_Image_W_Text)
        return f'./LineUpWithName_{timestamp}.png'
    else:
        return


def pullImage():
    Game_Dates = cellOperations.Get_Cell_Range(sheets.RSVP_SHEET_RANGE)[0]
    Earliest_Game_Date = Game_Dates[0]

    if Earliest_Game_Date:
        timestamp = (Earliest_Game_Date - datetime(1970, 1, 1)).total_seconds()
        return f'./LineUpWithName_{timestamp}.png'
    else:
        return
