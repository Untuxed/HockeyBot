from services.discordStuff import *
from services.sheets import *
from services.firebaseStuff import *
from utils.genericFunctions import get_season_id

@tree.command(name='importstats', description='Update player stats', guild=GUILD_ID)
async def importStats(interaction: discord.Interaction):
    # Send an initial response to the interaction
    await interaction.response.send_message("Updating player stats...", ephemeral=True)

    # Get the player stats from the Google Sheet
    response = SHEET.values().get(spreadsheetId=VOODOO_SHEET_ID, range=STATS_SHEET_RANGE).execute()
    stats_data = response.get('values', [])

    season_id = get_season_id(interaction)

    # Parse the stats data
    player_stats = {}
    for row in stats_data:
        number, first_name, last_name, gp, goals, assists, points, pims, plus_minus = row
        player_id = f"{first_name}_{last_name}_{number}"
        stats = {
            "GP": int(gp),
            "Goals": int(goals),
            "Assists": int(assists),
            "Points": int(points),
            "PIMs": int(pims),
            "Plus/Minus": int(plus_minus)
        }
        player_stats[player_id] = stats

    # Update the player stats in Firebase
    for player_id, stats in player_stats.items():
        db.collection(season_id).document('roster').collection('skaters').document(player_id).set({'stats': stats}, merge=True)

    # Edit the initial response to indicate that the player stats have been updated
    await interaction.edit_original_response(content="Player stats have been updated in Firebase.")