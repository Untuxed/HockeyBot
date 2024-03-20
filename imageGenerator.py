import cv2
from cellOperations import *

# Forwards Pixel Range 860 x 200 to 1950 x 715

Base_Lineup_Image = cv2.imread('./BaseLineupCard.png')

Font_Size = 1.2
Font_Weight = 2
Font_Color = (0, 0, 0)
Font_Type = cv2.FONT_HERSHEY_DUPLEX

Forwards = Get_Cell_Range(FORWARDS_LINEUP_RANGE)
Defense = [[item for item in sublist if item.strip()] for sublist in Get_Cell_Range(DEFENSE_LINEUP_RANGE)]
Goalie = Get_Cell_Range(GOALIE_LINEUP_RANGE)

Forward_Y_Spacing = int(515/len(Forwards))
Defense_Y_Spacing = int(500/len(Defense))

for i, Line in enumerate(Forwards):
    LW_Width = cv2.getTextSize(Line[0], Font_Type, fontScale=Font_Size, thickness=Font_Weight)
    C_Width = cv2.getTextSize(Line[1], Font_Type, fontScale=Font_Size, thickness=Font_Weight)
    RW_Width = cv2.getTextSize(Line[2], Font_Type, fontScale=Font_Size, thickness=Font_Weight)

    Lineup_Image_W_Text = cv2.putText(
        Base_Lineup_Image,
        Line[0],
        (int(860 + (375 - LW_Width[0][0])/2), 200 + i * Forward_Y_Spacing),
        fontFace=Font_Type,
        fontScale=Font_Size,
        color=Font_Color,
        thickness=Font_Weight
    )

    Lineup_Image_W_Text = cv2.putText(
        Base_Lineup_Image,
        Line[1],
        (int(1425 - C_Width[0][0]/2), 200 + i * Forward_Y_Spacing),
        fontFace=Font_Type,
        fontScale=Font_Size,
        color=Font_Color,
        thickness=Font_Weight
    )

    Lineup_Image_W_Text = cv2.putText(
        Base_Lineup_Image,
        Line[2],
        (int(1615 + (375 - RW_Width[0][0])/2), 200 + i * Forward_Y_Spacing),
        fontFace=Font_Type,
        fontScale=Font_Size,
        color=Font_Color,
        thickness=Font_Weight
    )

for i, Line in enumerate(Defense):
    LD_Width = cv2.getTextSize(Line[0], Font_Type, fontScale=Font_Size, thickness=Font_Weight)
    RD_Width = cv2.getTextSize(Line[1], Font_Type, fontScale=Font_Size, thickness=Font_Weight)

    Lineup_Image_W_Text = cv2.putText(
        Base_Lineup_Image,
        Line[0],
        (int(860 + (565 - LD_Width[0][0]) / 2), 870 + i * Defense_Y_Spacing),
        fontFace=Font_Type,
        fontScale=Font_Size,
        color=Font_Color,
        thickness=Font_Weight
    )

    Lineup_Image_W_Text = cv2.putText(
        Base_Lineup_Image,
        Line[1],
        (int(1425 + (565 - RD_Width[0][0]) / 2), 870 + i * Defense_Y_Spacing),
        fontFace=Font_Type,
        fontScale=Font_Size,
        color=Font_Color,
        thickness=Font_Weight
    )

Lineup_Image_W_Text = cv2.putText(
        Base_Lineup_Image,
        Goalie[0][0],
        (int(1425 - C_Width[0][0]/2), 1550),
        fontFace=Font_Type,
        fontScale=Font_Size,
        color=Font_Color,
        thickness=Font_Weight
    )

cv2.imwrite('./LineUpWithName.png', Lineup_Image_W_Text)
