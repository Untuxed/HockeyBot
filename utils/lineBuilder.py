from services.discordStuff import *
import re
from datetime import datetime, timedelta
from services.firebaseStuff import *
from utils.genericFunctions import get_season_and_game_id, create_ics_file


# region create RSVP document from sesh message
@hockeyBot.event
async def on_message(message):

    if message.author.name != 'sesh':
        return
    
    if isinstance(message.channel, discord.Thread):        
        if message.type == MessageType.thread_starter_message:
            # Get the role for the roster to mention from category name
            role_name = f"{message.channel.category.name} Roster"
            role = discord.utils.get(message.guild.roles, name=role_name)
            if role and message.author.name == 'sesh':
                # Send a message in the thread that mentions the role
                await message.channel.send(
                    f"{role.mention} The next game has been posted. To RSVP, go [HERE!](https://discord.com/channels/{message.guild.id}/{message.channel.parent.id}/{message.id})")
            return

    if message.embeds and not message.embeds[0].title.startswith(':calendar_spiral:'):
        print(message.embeds[0].title)
        return
    else:
    # if normal event creation message from sesh, create game documents in db
        season_id, game_id, gametime, opponent = get_season_and_game_id(message)
        
        ics_blob_filename = f'ICS_Files/{game_id}.ics'
        ics_as_bytes = create_ics_file(game_id, gametime, opponent)

        blob = bucket.blob(ics_blob_filename)  # Blob object for uploading images
        
        # Uploads image from filename and generates a url that can be used for embeds for 31 days by default
        blob.upload_from_string(ics_as_bytes, content_type='text/calendar')
        url = blob.generate_signed_url(expiration=timedelta(days=31))

        if season_id and game_id:
            db.collection(season_id).document('games').collection(game_id).document('RSVPs').set({})
            db.collection(season_id).document('games').collection(game_id).document('game-info').set({'gametime': gametime, 'opponent': opponent, 'discord_message_id': message.id, 'ics_url': url})


# endregion

# region get RSVPs on message edit (RSVP)
@hockeyBot.event
async def on_raw_message_edit(payload):
    if 'author' in payload.data and payload.data['author']['username'] == 'sesh':
        if payload.data['embeds'] and not payload.data['embeds'][0]['title'].startswith(':calendar_spiral:'):
            return

        messageID = int(payload.data['id'])
        channelID = int(payload.data['channel_id'])

        message = await hockeyBot.get_channel(channelID).fetch_message(messageID)

        # get season and document id's from the edited message
        season_id, game_id, gametime, opponent = get_season_and_game_id(message)

        # get the RSVP document from db
        rsvp_doc = db.collection(season_id).document('games').collection(game_id).document('RSVPs').get()

        if not rsvp_doc.exists:
            db.collection(season_id).document('games').collection(game_id).document('RSVPs').set({})
            db.collection(season_id).document('games').collection(game_id).document('game-info').set({'gametime': gametime, 'opponent': opponent, 'discord_message_id': message.id})

        # instantiate categories so it doesn't get mad
        for embed in message.embeds:
            attendees = []
            maybes = []
            nos = []

        # get the RSVPs from the edited message
        for field in embed.fields:
            if '✅ Attendees' in field.name:
                attendee_ids = re.findall(r'<@(\d+)>', field.value)
                attendees = [message.guild.get_member(int(id)).nick for id in attendee_ids]
            elif '🤷 Maybe' in field.name:
                maybe_ids = re.findall(r'<@(\d+)>', field.value)
                maybes = [message.guild.get_member(int(id)).nick for id in maybe_ids]
            elif '❌ No' in field.name:
                no_ids = re.findall(r'<@(\d+)>', field.value)
                nos = [message.guild.get_member(int(id)).nick for id in no_ids]

            # Update the document in Firebase
            db.collection(season_id).document('games').collection(game_id).document('RSVPs').update({
                'attendees': attendees,
                'maybes': maybes,
                'nos': nos
            })
# endregion
