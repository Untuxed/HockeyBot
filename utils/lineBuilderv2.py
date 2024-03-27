from services.discordStuff import *
import re
from datetime import datetime, timedelta
from services.firebaseStuff import *


#region extract game info and create db document in lines collection to store RSVP data
@hockeyBot.event
async def on_message(message):
    if message.author.name == 'sesh':
        category_name = message.channel.category.name #season_id gets created from category name in discord
        season_id = re.sub(r'\s+', '_', category_name).lower()

        #get game information from embed to use as document id
        for embed in message.embeds:
            game_title = embed.title
            match = re.search(r':calendar_spiral:  \*\*Game (\d+) vs\. (.+?)\*\*', game_title)
            if match:
                game_number = match.group(1)
                opponent = match.group(2)
        for field in embed.fields:
            if field.name == 'Time':
                match = re.search(r'<t:(\d+):F>', field.value)
                if match:
                    timestamp = int(match.group(1))
                    game_time = datetime.utcfromtimestamp(timestamp) - timedelta(hours=4)
                    formatted_time = game_time.strftime('%m-%d-%Y')
        
        #create an empty lines document for this game
        doc_id = f'game_{game_number}_vs_{opponent}_{formatted_time}'
        db.collection(season_id).document('games').collection(doc_id).document('lines').set({})
#endregion
        
#region extract RSVP data on edit
@hockeyBot.event
async def on_message_edit(before, after):
    if before.author.name == 'sesh':

        for embed in after.embeds:
            print(f'Fields:')
            for field in embed.fields:
                print(f'  {field.name}: {field.value}')


        # Extract RSVP info from the embed fields
        # for embed in after.embeds:
        #     attendees = []
        #     maybes = []
        #     nos = []
        #     for field in embed.fields:
        #         if field.name.startswith('✅ Attendees'):
        #             attendees = field.value.split('> ')[1].split('\n') if field.value != '> -' else []
        #         elif field.name.startswith('🤷 Maybe'):
        #             maybes = field.value.split('> ')[1].split('\n') if field.value != '> -' else []
        #         elif field.name.startswith('❌ No'):
        #             nos = field.value.split('> ')[1].split('\n') if field.value != '> -' else []

        #     print(f'Attendees: {attendees}')
        #     print(f'Maybes: {maybes}')
        #     print(f'Nos: {nos}')
#endregion


#region example of sesh embed structure
    # SESH EMBED STRUCTURE
        # for embed in message.embeds:
        #     print(f'Title: {embed.title}')
        #     print(f'Description: {embed.description}')
        #     print(f'URL: {embed.url}')
        #     print(f'Timestamp: {embed.timestamp}')
        #     print(f'Color: {embed.color}')
        #     print(f'Footer: {embed.footer.text}')
        #     print(f'Image: {embed.image.url}')
        #     print(f'Thumbnail: {embed.thumbnail.url}')
        #     print(f'Author: {embed.author.name}')
        #     print(f'Fields:')
        #     for field in embed.fields:
        #         print(f'  {field.name}: {field.value}')

    # Title: :calendar_spiral:  **Game # vs. Opponent**
    # Description: None
    # URL: None
    # Timestamp: None
    # Color: #00f4ff
    # Footer: ⚙️ Settings | Created by Marino McGalla [7]
    # Image: None
    # Thumbnail: None
    # Author: None
    # Fields:
    #   Time: <t:1711425079:F> (<t:1711425079:R>) [[+]](http://www.google.com/calendar/event?action=TEMPLATE&text=Game%20%23%20vs.%20Opponent&dates=20240326T035119Z/20240326T045119Z&details=&location=)
    #   ✅ Attendees (0): > -
    #   🤷 Maybe (0): > -
    #   ❌ No (0): > -
#endregion