from services.discordStuff import *
from services.sheets import *
from services.cellOperations import *
from services.firebaseStuff import *
from utils.genericFunctions import get_pending, get_roster

@tree.command(name='importrsvps', description='Import RSVPs for a game', guild=GUILD_ID)
async def importRsvps(interaction: discord.Interaction, game_id: str):
    await interaction.response.defer()
    # Define reference to correct db collection using the game id and season id
    season_id = interaction.channel.category.name.lower().replace(' ', '_')
    rsvp_ref = db.collection(season_id).document('games').collection(game_id).document('RSVPs')

    # Get the RSVP'd players for each category attendees, nos, and maybes
    rsvp_doc = rsvp_ref.get()
    if rsvp_doc.exists:
        rsvp_data = rsvp_doc.to_dict()
        attendees = rsvp_data.get('attendees', [])
        maybes = rsvp_data.get('maybes', [])
        nos = rsvp_data.get('nos', [])

        rostered_skaters, rostered_goalies = get_roster(interaction)
        full_roster = rostered_skaters + rostered_goalies

        # Define the ranges
        attendees_range = 'Lineup!E3:E15'
        maybes_range = 'Lineup!F3:F15'
        nos_range = 'Lineup!G3:G15'
        pending_response_range = 'Lineup!H3:H15'

        pendings = get_pending(attendees, maybes, nos, full_roster)

        # Clear the cells in the ranges
        await Range_Clear([attendees_range, maybes_range, nos_range, pending_response_range])

        # Write the RSVPs to the Google Sheet
        SHEET.values().update(spreadsheetId=VOODOO_SHEET_ID, range=attendees_range, valueInputOption='USER_ENTERED',
                              body={'values': [[name] for name in attendees]}).execute()
        SHEET.values().update(spreadsheetId=VOODOO_SHEET_ID, range=maybes_range, valueInputOption='USER_ENTERED',
                              body={'values': [[name] for name in maybes]}).execute()
        SHEET.values().update(spreadsheetId=VOODOO_SHEET_ID, range=nos_range, valueInputOption='USER_ENTERED',
                              body={'values': [[name] for name in nos]}).execute()
        SHEET.values().update(spreadsheetId=VOODOO_SHEET_ID, range=pending_response_range,
                              valueInputOption='USER_ENTERED', body={'values': [[name] for name in pendings]}).execute()

        await interaction.followup.send(f"RSVPs for game {game_id} have been imported to the Google Sheet.")
    else:
        await interaction.followup.send(f"No RSVPs found for game {game_id}.")