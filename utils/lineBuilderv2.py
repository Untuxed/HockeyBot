from services.discordStuff import *
import re
from datetime import datetime, timedelta
from services.firebaseStuff import *
from utils.genericFunctions import get_season_and_game_id

#region create RSVP document from sesh message
@hockeyBot.event
async def on_message(message):
    if message.author.name == 'sesh':
        season_id, doc_id = get_season_and_game_id(message)
        db.collection(season_id).document('games').collection(doc_id).document('RSVPs').set({})
#endregion
        
#region get RSVPs on message edit (RSVP)
@hockeyBot.event
async def on_message_edit(before, after):
    if before.author.name == 'sesh':

        #get season and document id's from the edited message
        season_id, doc_id = get_season_and_game_id(after)

        #get the RSVP document from db
        rsvp_doc = db.collection(season_id).document('games').collection(doc_id).document('RSVPs').get()

        #instantiate categories so it doesn't get mad
        for embed in after.embeds:
            attendees = []
            maybes = []
            nos = []

        # get the RSVPs from the edited message
        for field in embed.fields:
            if '✅ Attendees' in field.name:
                attendee_ids = re.findall(r'<@(\d+)>', field.value)
                attendees = [after.guild.get_member(int(id)).nick for id in attendee_ids]
            elif '🤷 Maybe' in field.name:
                maybe_ids = re.findall(r'<@(\d+)>', field.value)
                maybes = [after.guild.get_member(int(id)).nick for id in maybe_ids]
            elif '❌ No' in field.name:
                no_ids = re.findall(r'<@(\d+)>', field.value)
                nos = [after.guild.get_member(int(id)).nick for id in no_ids]

            # Update the document in Firebase
            db.collection(season_id).document('games').collection(doc_id).document('RSVPs').update({
                'attendees': attendees,
                'maybes': maybes,
                'nos': nos
            })
#endregion