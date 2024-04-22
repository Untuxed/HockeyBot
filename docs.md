# General Commands

## /getmystats
- Description: Returns the players stats as a private message. Restricted to players that are on the roster including subs.
- Usage: /getmystats
  
## /getplayerstats 
- Description: Returns a players stats as a private message, if the player is on the roster. Otherwise it returns an error message. Anyone can use this command.
- Usage: /getplayerstats [discord.member: discord user]

## /getlines
- Description: Sends the lineup for the next game as a private message. This command only works if the lineup has been previously set using the captain command '/setlines'. Otherwise, it responds with an error message.
- Usage: /getlines

## /getgametime
- Description: Returns the date, time, and opponent of the next game in the schedule. This command will only work when it is used in a text channel associated with a season. The bot will inform the user if it is used in an incorrect channel.
- Usage: /getgametime

## /avatar
- Description: Sends the avatar image of the specified user back to the channel it was used in.
- Usage: /avatar [discord.member: discord user]

# Captain Commands
## /setlines 
- Description: Retrieves and displays information about the next scheduled game based on data from a Google Sheet. Additionally, it generates a custom lineup image based on the number of lines present in the Google Sheet. In the event that there are no upcoming games or the bot encounters an issue while generating the image, it will respond with an error message.
- Usage: /setlines

## /addplayer
- Description: Adds a player to the Firebase roster and statistical database. It uses the category name as the season ID. The player's nickname in discord has to be in the format: player's firstname player's lastname [player's number]. If this format is followed the bot gets all of the required information (player's Discord ID, number, first name, last name, position, stats, if they are a captain, and their handedness) from their name and roles on discord. This command also separates the skaters and the goalies into separate Firebase document pages. If adding the player is successful, it will return a success message; if it fails, the bot will send an error message.
- Usage: /addplayer [discord.member: discord user]

## /addnormie
- Description: This command should only be used in cases where someone is not in the discord server, this command can be easily screwed up and cause complications in the database. This command functions in the same way as /addplayer but all of the players data must be input mannually.
- Usage: /addnormie [str: first name] [str: last name] [str: number] [str: postition] [str: status] [bool: is captain] [str: handedness]

## /importrsvps
- Description: Command which will be depreciated in the next update of the bot. Manually transfers the RSVPs from the Firebase DB to the google sheet. In the future this will automatically happen in on_raw_message_edit. It uses the game ID (date of the game in MM-DD-YYYY format) as an argument to ensure that the correct RSVPs are imported.
- Usage: /importrsvps [str: game id (Date in MM-DD-YYYY format)]

# Utils 
# Generic Functions #
## checkDuplicatePlayer(collection_name: str, player_id: str)
- Description: This function checks for the existence of a player ID within a specified collection in the database.
- Usage: The below code will check if a player with the ID "player123" exists in the "players" collection within the Firebase DB. It returns True if the player ID already exists, otherwise False.
  ```python
  is_duplicate = checkDuplicatePlayer("players", "player123")
  ```
  

