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

# Captain Commands
## /setlines 
- Description: Retrieves and displays information about the next scheduled game based on data from a Google Sheet. Additionally, it generates a custom lineup image based on the number of lines present in the Google Sheet. In the event that there are no upcoming games or the bot encounters an issue while generating the image, it will respond with an error message.
- Usage: /setlines

## /addplayer
- Description: Adds a player to the Firebase roster and statistical database. It uses the category name as the season ID. The player's nickname in discord has to be in the format: player's firstname player's lastname [player's number]. If this format is followed the bot gets all of the required information (player's Discord ID, number, first name, last name, position, stats, if they are a captain, and their handedness) from their name and roles on discord. This command also separates the skaters and the goalies into separate Firebase document pages. If adding the player is successful, it will return a success message; if it fails, the bot will send an error message.
- Usage: /addplayer [discord.member: discord user]
