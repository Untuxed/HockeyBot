from services.discordStuff import *
import re
from datetime import datetime, timedelta
from services.firebaseStuff import *
from utils.genericFunctions import get_season_and_game_id


# region create RSVP document from sesh message
@hockeyBot.event
async def on_message(message):
    if message.author.name != 'sesh':
        return
    if message.author.name == 'sesh':
        # Ignore "event is starting now" messages, can remove once we convert to firebase entirely
        for embed in message.embeds:
            if embed.title.endswith('is starting now!'):
                return
                # If the message is in a thread
    if isinstance(message.channel, discord.Thread):
        # Ignore messages in the thread sent by the bot
        if message.author == hockeyBot.user:
            return
        # Get the role for the roster to mention from category name
        role_name = f"{message.channel.category.name} Roster"
        role = discord.utils.get(message.guild.roles, name=role_name)
        if role and message.author.name == 'sesh':
            # Send a message in the thread that mentions the role
            await message.channel.send(
                f"{role.mention} The next game has been posted. To RSVP, go [HERE!](https://discord.com/channels/{message.guild.id}/{message.channel.parent.id}/{message.id})")
        return
    # if normal event creation message from sesh, create game documents in db
    season_id, doc_id = get_season_and_game_id(message)
    if season_id and doc_id:
        db.collection(season_id).document('games').collection(doc_id).document('RSVPs').set({})
        db.collection(season_id).document('games').collection(doc_id).document('discordMessageID').set({message.id})


# endregion

# region get RSVPs on message edit (RSVP)
@hockeyBot.event
async def on_raw_message_edit(payload):
    if payload.data['author']['username'] == 'sesh':

        ID = int(payload.data['id'])

        message = await discord.utils.get(hockeyBot.guilds[1].text_channels, name='dev-schedule').fetch_message(ID)

        # get season and document id's from the edited message
        season_id, doc_id = get_season_and_game_id(message)

        # get the RSVP document from db
        rsvp_doc = db.collection(season_id).document('games').collection(doc_id).document('RSVPs').get()

        if not rsvp_doc.exists:
            db.collection(season_id).document('games').collection(doc_id).document('RSVPs').set({})
            db.collection(season_id).document('games').collection(doc_id).document('discordMessageID').set({ID})

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
            db.collection(season_id).document('games').collection(doc_id).document('RSVPs').update({
                'attendees': attendees,
                'maybes': maybes,
                'nos': nos
            })
# endregion
