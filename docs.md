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
- Parameters:
  - collection_name (str): The name of the collection in the Firestore database where the player data is stored.
  - player_id (str): The unique identifier of the player whose existence needs to be checked within the specified collection.
- Usage: The below code will check if a player with the ID "player123" exists in the "players" collection within the Firebase DB. It returns True if the player ID already exists, otherwise False.
  ```python
  is_duplicate = checkDuplicatePlayer("players", "player123")
  ```

## get_player_data(interaction, first_name=None, last_name=None, number=None)
- Description: Retrieves data of a player from Firebase DB. This function is called by both commands.getMyStats and commands.getPlayerStats. In the case of getMyStats it uses the users discord nickname to get their information. For getPlayerStats the players information is unpacked from the specified member in the getPlayerStats function and the stats are retrieved using that information. This code gets the season ID from the channel that it was called in. It then fetches the player's statistics.
If the player data is found and contains statistics, it returns a dictionary containing the player's statistics data along with first name, last name, and number. If the player data is not found or does not contain statistics, it returns None.
- Parameters:
  - interaction: The interaction object representing the context of the command.
  - first_name (optional): The first name of the player.
  - last_name (optional): The last name of the player.
  - number (optional): The number associated with the player.
- Usage: This retrieves the statistics data of the player named "Sidney Crosby" with number "87" for the current season. 
  ```python
  player_data = await get_player_data(interaction, first_name="Sidney", last_name="Crosby", number="87")
  ```
  This will retrieve the stats data of the player who sent the message stored in the discord.interaction argument.
  ```python
  player_data = await get_player_data(interaction)
  ```

## generate_stats_message(stats_data: dict)
- Description: This function generates a formatted message containing statistics data for a player, which is then sent using commands.getMyStats and commands.getPlayerStats.  It takes a dictionary `stats_data` as input, which must contain the player's first name, last name, and various statistics such as games played (GP), goals, assists, points, points per game (PPG), plus/minus, and penalties in minutes (PIMs). The function constructs a message with these statistics in a readable format.
- Parameters:
  - stats_data (dict): A dictionary containing the player's statistics data, including keys such as 'first_name', 'last_name', 'GP', 'Goals', 'Assists', 'Points', 'PPG', 'Plus/Minus', and 'PIMs'.
- Usage: This should only be called by another function where the stats dictionary is properly formatted. If the stats message is not properly formatted this will cause an error.

## get_season_and_game_id(message)
- Description: This function extracts the season ID, game ID, game time, and opponent from a sesh event message. It utilizes the `get_season_id()` function to retrieve the season ID from the event. By default season ID is the category name in discord. It then parses information from the embed within the message to extract the game title, time, and opponent. The game ID is generated based on the formatted game time. Finally, it returns the extracted season ID, game ID, game time, and opponent. This function will work with a malformed sesh ecent message, although the opponent name will not be displayed properly. 
- Parameters:
  - message: The sesh event object containing information about the game.
- Usage: The below will return all of the information to separate values which can then be used elsewhere.
  ```python
  season_id, game_id, game_time, opponent = get_season_and_game_id(message)
  ```
  This will return a list object with each of the variables as an index.
  ```python
  game_information = get_season_and_game_id(message)
  ```

## get_season_id(messageish)
- Description: This function extracts the season ID (by default the category name in discord server) from a discord.message or discord.interaction object. It retrieves the category name of the channel from which the message is sent and formats it into a suitable season ID format. The season ID is created by replacing whitespace with underscores and converting to lowercase.
- Parameters:
  - messageish: The discord.message or discord.interaction object from which the season ID (category name in discord server) is to be extracted.
- Usage: This returns the season_id for the discord channel where messageish was typed in.
  ```python
  season_id = get_season_id(messageish)
  ```

## get_game_date(interaction)
- Description: This function retrieves the date, time, and opponent of the next game from the Firestore database based on the discord.interaction that is passed in as an argument. It exclusively returns the date, time, and opponent of the next game only. 
- Parameters:
  - interaction: The interaction object representing the context of the command.
- Usage: The below will return all of the information as individual variables.
  ```python
  next_game_date, next_game_time, opponent = get_game_date(interaction)
  ```
  This will return a list object with each of the variables as an index.
  ```python
  next_game_date, next_game_time, opponent = get_game_date(interaction)
  ```

## get_roster(interaction)
- Description: This function retrieves the roster of skaters and goalies for a season based on the category that it is called in, this function will be updated to specify a specific season if the user wants. It queries the Firestore database to retrieve the skaters and goalies roster collections separately.
- Parameters:
  - interaction: The interaction object representing the context of the command.
- Usage: The below usage returns Firestore.object files which must be translated to dictionary objects to iterate through later on. Returning them as objects is probably the most efficent usage of this function though.
  ```python
  skaters_stream, goalies_stream = get_roster(interaction)
  ```
