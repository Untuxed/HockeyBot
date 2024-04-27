from services.discordStuff import *
from services.sheets import *
from services.firebaseStuff import *
from utils.genericFunctions import get_season_id

@tree.command(name='importstats', description='Update player stats', guild=GUILD_ID)
async def importStats(interaction: discord.Interaction):
    # Send an initial response to the interaction
    await interaction.response.send_message("Updating player stats...", ephemeral=True)

    # Get the player stats from the Google Sheet
    skaters_response = SHEET.values().get(spreadsheetId=VOODOO_SHEET_ID, range=SKATERS_STATS_SHEET_RANGE).execute()
    skaters_stats_data = skaters_response.get('values', [])

    goalie_response = SHEET.values().get(spreadsheetId=VOODOO_SHEET_ID, range=GOALIES_STATS_SHEET_RANGE).execute()
    goalie_stats_data = goalie_response.get('values', [])

    season_id = get_season_id(interaction)

    # Parse the stats data
    for row in skaters_stats_data:
        number, first_name, last_name, gp, goals, assists, points, pims, plus_minus, ppg = row
        player_id = f"{first_name}_{last_name}_{number}"
        stats = {
            "GP": int(gp),
            "Goals": int(goals),
            "Assists": int(assists),
            "Points": int(points),
            "PIMs": int(pims),
            "Plus/Minus": int(plus_minus),
            "PPG": float(ppg)
        }
        db.collection(season_id).document('roster').collection('skaters').document(player_id).set({'stats': stats}, merge=True)

    for row in goalie_stats_data:
        number, first_name, last_name, gp, ga, gaa, w, l, pims = row
        player_id = f"{first_name}_{last_name}_{number}"
        stats = {
            "GP": int(gp),
            "GA": int(ga),
            "GAA": float(gaa),
            "Wins": int(w),
            "Losses": int(l),
            "PIMs": int(pims)
        }
        db.collection(season_id).document('roster').collection('goalies').document(player_id).set({'stats': stats}, merge=True)

    # Edit the initial response to indicate that the player stats have been updated
    await interaction.edit_original_response(content="Player stats have been updated in Firebase.")