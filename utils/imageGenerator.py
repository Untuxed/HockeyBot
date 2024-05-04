import cv2
from datetime import datetime, timedelta
from utils.genericFunctions import get_game_date, get_roster, get_season_id
import services.cellOperations as cellOperations
import services.sheets as sheets
import random
from services.firebaseStuff import *
import cairosvg
import re


# region Lineup image generation code
async def imageGenerator(interaction):
    """
    Generates lineup images for the specified team using a discord interaction. The season ID and team ID is taken from the channel that the message is called in, the lineup on the google sheet (TODO: Convert this to a web based front end). If the player exists in the firebase roster their number is taken from there from one of the private functions. The images that this function generates are uploaded to firebase to limit the amount of interactions with firebase. The signed URL that is used is good for 31 days by default (TODO: Decided if this how we want to do this forever).

    Parameters:
        interaction (discord.Interaction): The interaction object representing the discord command interaction.

    Returns:
        bool: True if the lineup images are images are generated successfully, False otherwise.
    """
    def rosterLookup(playerName, roster):
        """
        Looks up a player's information in the firebase roster.

        Parameters:
            playerName (str): The name of the player to look up. (TODO: convert this to using the playerIDs that we need to properly format)
            roster (list): A list of player dictionaries containing roster data data.

        Returns:
            str: The player's number followed by their name if found, otherwise '## - playerName'.
        """
        if playerName:  # Check if the name that is passed into the function is not None
            for _, playerData in enumerate(roster):  # Iterates through the roster list, used to use player index but that has been depreciated
                
                # Split playerData by spaces and remove brackets, then extract the number part
                name_parts = playerData.replace('[', '').replace(']', '').split(' ')
                _, _, number = name_parts[:3]

                # Check if playerName (passed) is present in playerData (iterated roster player)
                if playerName in playerData:
                    return f'{number} - ' + playerName  # Return player's number and name
            return '## - ' + playerName  # If player is not found, return placeholder
        else:
            return ' '  # Return empty string if playerName is empty

    def randomTextColor():
        """
        Generates a random RGB color for text in the custom lineup card.

        Returns:
            tuple: A tuple representing the RGB color values.
        """
        return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)

    def addGameInfo(baseSVGFile, newImageFilePath, opponentName, gameTime, gameDate):
        """
        Adds game information to an SVG file by editing the SVG file as a text file and replacing known variables with game specific information. It then converts the SVG file with that information to a PNG for storage and distribution. Saves a temporary version of the lineup card to disk.

        Parameters:
            baseSVGFile (str): The path to the base SVG file.
            newImageFilePath (str): The path to save the new image file.
            opponentName (str): The name of the opponent team.
            gameTime (str): The time of the game.
            gameDate (datetime.datetime): The date of the game.

        Returns:
            None
        """
        temp_SVG_FilePath = './resources/images/temp.svg'  # Temporary SVG file path

        gameDate = gameDate.strftime('%m-%d')  # Format game date

        # Replace placeholder in the base SVG file with game information
        SVG_Game_Info = baseSVGFile.replace('### REPLACE ME ###', opponentName[3:-2] + ': ' + gameDate + ', ' + gameTime)

        # Write the modified SVG content to a temporary SVG file
        with open(temp_SVG_FilePath, 'w') as file:
            file.write(SVG_Game_Info)

        # Convert the temporary SVG file to PNG format and save it to the new image file path
        cairosvg.svg2png(url=temp_SVG_FilePath, write_to=newImageFilePath)

    def addPlayerLineup(baseImage, playerText, x_anchor, y_location, Font_Color=(0, 0, 0)):
        """
        Adds player lineup text from rosterLookup() to the lineup image for distribution.

        Parameters:
            baseImage (numpy.ndarray): The base lineup image from addGameInfo() to which the text will be added.
            playerText (str): The text to be added to the image.
            x_anchor (int): The x-coordinate of the anchor point for the text.
            y_location (int): The y-coordinate of the anchor point for the text.
            Font_Color (tuple, optional): The RGB color tuple for the text. Defaults to (0, 0, 0).

        Returns:
            numpy.ndarray: The image with the added text.
        """
        Font_Size = 1.5  # Font size
        Font_Weight = 3  # Font weight
        Font_Type = cv2.FONT_HERSHEY_DUPLEX  # Font type

        # Gets the width of the text so it can be placed evenly on the image
        text_Width = cv2.getTextSize(playerText, Font_Type, fontScale=Font_Size, thickness=Font_Weight)

        # Add the text to the image
        return cv2.putText(
            baseImage,
            playerText,
            (int(x_anchor - (text_Width[0][0] / 2)), y_location),
            fontFace=Font_Type,
            fontScale=Font_Size,
            color=Font_Color,
            thickness=Font_Weight
        )

    def writeTempFiles(description, custom=''):
        """
        Writes temporary files and updates Firebase database.

        Parameters:
            desc (str): Description for the file in firebase, this might not be necessary.
            custom (str, optional): Custom prefix for file and database fields. Defaults to ''.

        Returns:
            None
        """
        # Sets the filename for storage on firebase filepath
        image_blob_name = f'LineupImages/{custom}lineupWithName_{game_id}.png'

        # Firebase database reference for the lineup card
        image_firebase_database_reference = db.collection(season_id).document('games').collection(game_id).document('Lineup_Cards')

        filename = f'./resources/images/temp_{custom}BaseLineupCard.png'  # Grabs the temporary written after all the players and numbers have been added
        blob = bucket.blob(image_blob_name)  # Blob object for uploading images
        
        # Uploads image from filename and generates a url that can be used for embeds for 31 days by default
        blob.upload_from_filename(filename)
        url = blob.generate_signed_url(expiration=timedelta(days=31))

        # Check if lineup document exists in Firebase database
        lineup_doc = db.collection(season_id).document('games').collection(game_id).document('Lineup_Cards').get()
        
        if not lineup_doc.exists:
            # If lineup document does not exist, set database fields
            image_firebase_database_reference.set({
                f'{custom}image_url': image_blob_name,
                f'{custom}description': description,
                f'{custom}signed_url': url
            })
        else:
            # If lineup document exists, update database fields
            image_firebase_database_reference.update({
                f'{custom}image_url': image_blob_name,
                f'{custom}description': description,
                f'{custom}signed_url': url
            })
        return


    next_game_date, next_game_time, opponent = get_game_date(interaction)  # Get next game date, time, and opponent

    Base_Lineup_Image_Path = 'LineupImages/BaseLineupCard.svg'  # Path to normal lineup card SVG
    Dennis_Base_Lineup_Image_Path = 'LineupImages/Dennis_BaseLineupCard.svg'  # Path to Dennis lineup card SVG

    # Download the base lineup card in SVG format from Firebase
    Base_Lineup_Image = bucket.blob(Base_Lineup_Image_Path).download_as_text()
    Dennis_Base_Lineup_Image = bucket.blob(Dennis_Base_Lineup_Image_Path).download_as_text()

    # Check if there is a next game date and time
    if next_game_time and next_game_date:
        # If there is a next game and time add that information to both lineup cards
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
        return  # Return if there's no next game date or time

    # Get rostered skaters and goalies from the Firebase db
    rosteredSkaters, rosteredGoalies = get_roster(interaction)

    # Get forward lineup data from the google sheet and set default to ' ' if there is no one in the slot
    Forwards = [
        [
            name.split()[0] if name else '' for name in sublist
        ] for sublist in cellOperations.Get_Cell_Range(sheets.FORWARDS_LINEUP_RANGE)]
    
    # If no forwards have been set in the sheet default it to the four line format
    if not Forwards:
        Forwards = [
            ['Player #1', 'Player #2', 'Player #3'],
            ['Player #4', 'Player #5', 'Player #6'],
            ['Player #7', 'Player #8', 'Player #9'],
            ['Player #10', 'Player #11', 'Player #12']
        ]

    # Get defense lineup data from the google sheet
    Defense = [
        [
            item for item in sublist if item.strip()
        ] for sublist in cellOperations.Get_Cell_Range(sheets.DEFENSE_LINEUP_RANGE)]
    Defense = [[name.split()[0] for name in sublist] for sublist in Defense]

    # If no defensmen have been set in the sheet default it to the three line format
    if not Defense:
        Defense = [
            ['Player #1', 'Player #2'],
            ['Player #3', 'Player #4'],
            ['Player #5', 'Player #6']
        ]

    # Get goalie lineup data from the google sheet 
    Goalie = [
        [
            name.split()[0] if name else '' for name in sublist
        ] for sublist in cellOperations.Get_Cell_Range(sheets.GOALIE_LINEUP_RANGE)]

    # If no goalie has been set it defaults to Goalie #1
    if not Goalie:
        Goalie = [[' ', 'Goalie #1', ' ']]

    # Calculate spacing for forwards and defense lineup
    Forward_Y_Spacing = int(515 / len(Forwards))
    Defense_Y_Spacing = int(500 / len(Defense))

    # Read the lineup cards that were cached on the disk after the game information has been placed on them
    Base_Lineup_Image = cv2.imread('./resources/images/temp_BaseLineupCard.png')
    Dennis_Base_Lineup_Image = cv2.imread('./resources/images/temp_Dennis_BaseLineupCard.png')

    # Adds the player data in the format (## - First name) for the forwards to both lineup cards (Dennis lineup card gets random colors)
    for Line_Number, Line in enumerate(Forwards):
        # Get all of the forwards in the format ## - Firstname
        LW_Text = rosterLookup(Line[0], rosteredSkaters)
        C_Text = rosterLookup(Line[1], rosteredSkaters)
        RW_Text = rosterLookup(Line[2], rosteredSkaters)

        # Adds the text to the base lineup card
        _ = addPlayerLineup(Base_Lineup_Image, LW_Text, 947.5, 200 + Line_Number * Forward_Y_Spacing)
        _ = addPlayerLineup(Base_Lineup_Image, C_Text, 1327.5, 200 + Line_Number * Forward_Y_Spacing)
        _ = addPlayerLineup(Base_Lineup_Image, RW_Text, 1702.5, 200 + Line_Number * Forward_Y_Spacing)

        # Adds the text to the dennis lineup card with random colors to them
        _ = addPlayerLineup(Dennis_Base_Lineup_Image, LW_Text, 947.5, 200 + Line_Number * Forward_Y_Spacing, randomTextColor())
        _ = addPlayerLineup(Dennis_Base_Lineup_Image, C_Text, 1327.5, 200 + Line_Number * Forward_Y_Spacing, randomTextColor())
        _ = addPlayerLineup(Dennis_Base_Lineup_Image, RW_Text, 1702.5, 200 + Line_Number * Forward_Y_Spacing, randomTextColor())

    # Adds the player data in the format (## - First name) for the defense to both lineup cards (Dennis lineup card gets random colors)
    for Line_Number, Line in enumerate(Defense):
        # Gets the defense data in the format ## - Firstname
        LD_Text = rosterLookup(Line[0], rosteredSkaters)
        RD_Text = rosterLookup(Line[1], rosteredSkaters)

        # Adds the text to the base lineup card
        _ = addPlayerLineup(Base_Lineup_Image, LD_Text, 947.5, 870 + Line_Number * Defense_Y_Spacing)
        _ = addPlayerLineup(Base_Lineup_Image, RD_Text, 1611.25, 870 + Line_Number * Defense_Y_Spacing)

        # Adds the text to the dennis lineup card with random colors to them
        _ = addPlayerLineup(Dennis_Base_Lineup_Image, LD_Text, 947.5, 870 + Line_Number * Forward_Y_Spacing, randomTextColor())
        _ = addPlayerLineup(Dennis_Base_Lineup_Image, RD_Text, 1611.25, 870 + Line_Number * Forward_Y_Spacing, randomTextColor())

    # Get goalie text
    G_Text = rosterLookup(Goalie[0][1], rosteredGoalies)

    # Adds the goalie information to both of the lineup cards
    Lineup_Image_W_Text = addPlayerLineup(Base_Lineup_Image, G_Text, 1327.5, 1500)
    Dennis_Lineup_Image_W_Text = addPlayerLineup(Dennis_Base_Lineup_Image, G_Text, 1327.5, 1500, randomTextColor())

    # Gets the season ID from the interaction
    season_id = get_season_id(interaction)

    # Check if there is a next game in the database
    if next_game_date:
        game_id = next_game_date.strftime('%m-%d-%Y')  # Formats the data into the game ID

        # Caches both lineup cards to disk
        cv2.imwrite(f'./resources/images/temp_BaseLineupCard.png', Lineup_Image_W_Text)
        cv2.imwrite(f'./resources/images/temp_Dennis_BaseLineupCard.png', Dennis_Lineup_Image_W_Text)

        # Uploads the images to Firebase and saves their URLs for the embeds later
        writeTempFiles(desc='Basic Lineup Card')
        writeTempFiles(desc='Dennis Lineup Card', custom='Dennis_')

        return True  # Return True if successful
    else:
        return False  # Return False if there's no next game date
# endregion     


# region Pull image region
def pullImage(interaction):
    """
    Gets the URL for the images that were previously generated by imageGenerator

    Parameters:
        interaction (discord.Interaction): The interaction object representing the discord command interaction.

    Returns:
        tuple: A tuple containing the signed URL for the lineup card, the signed URL for the Dennis lineup card,
               and the message ID if available (TODO: There should always be a messageID available but maybe not all the time).
    """
    next_game_date, _, _ = get_game_date(interaction)  # Get the next game date
    if next_game_date is None:
        return None, None  # Return None if there's no next game date
    
    game_id = next_game_date.strftime('%m-%d-%Y')  # Format game ID

    category_name = interaction.channel.category.name  # Get the category name
    season_id = re.sub(r'\s+', '_', category_name).lower()  # Format season ID

    # Get lineup card information from Firebase
    lineup_card_dict = db.collection(season_id).document('games').collection(game_id).document('Lineup_Cards').get().to_dict()

    if next_game_date:
        if 'messageID' in lineup_card_dict:
            # Returns tuple of the urls and discord message ID if the  message ID exists
            return lineup_card_dict['signed_url'], lineup_card_dict['Dennis_image_url'], lineup_card_dict['messageID']
        else:
            return lineup_card_dict['signed_url'], lineup_card_dict['Dennis_image_url'], None  # Returns tuple of the urls if the message ID doesn't exist
    else:
        return  # Return None if there's no next game date
#endregion
    