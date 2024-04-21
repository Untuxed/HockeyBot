from services.discordStuff import *
from services.sheets import *
from services.cellOperations import *
from services.firebaseStuff import *

@tree.command(name='importrsvps', description='Import RSVPs for a game', guild=GUILD_ID)
async def importRsvps(interaction: discord.Interaction, game_id: str):
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

        # Define the ranges
        attendees_range = 'Lineup!E3:E15'
        maybes_range = 'Lineup!F3:F15'
        nos_range = 'Lineup!G3:G15'

        # Clear the cells in the ranges
        await Range_Clear([attendees_range, maybes_range, nos_range])

        # Write the RSVPs to the Google Sheet
        SHEET.values().update(spreadsheetId=VOODOO_SHEET_ID, range=attendees_range, valueInputOption='USER_ENTERED',
                              body={'values': [[name] for name in attendees]}).execute()
        SHEET.values().update(spreadsheetId=VOODOO_SHEET_ID, range=maybes_range, valueInputOption='USER_ENTERED',
                              body={'values': [[name] for name in maybes]}).execute()
        SHEET.values().update(spreadsheetId=VOODOO_SHEET_ID, range=nos_range, valueInputOption='USER_ENTERED',
                              body={'values': [[name] for name in nos]}).execute()

        await interaction.response.send_message(f"RSVPs for game {game_id} have been imported to the Google Sheet.")
    else:
        await interaction.response.send_message(f"No RSVPs found for game {game_id}.")