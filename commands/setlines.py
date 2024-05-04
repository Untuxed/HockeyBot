from services.discordStuff import *
from utils.imageGenerator import imageGenerator, pullImage, get_game_date
from services.firebaseStuff import *
import re

@tree.command(
    name='setlines',
    description='Set lineup from the google sheet, generates lineup card image, responds with lineup card image.',
    guild=GUILD_ID
)
async def setLines(interaction: discord.Interaction):
    did_write_file = await imageGenerator(interaction)

    if not did_write_file:
        await interaction.followup.send('Something went wrong, looking into it.')

    base_URL, _, _ = pullImage(interaction)

    if not base_URL:
        await interaction.followup.send('Something went wrong, looking into it.')
    else:
        lineup_embed = discord.Embed(title='Lineup Embed Test 1', description='This is a test of the embed system')
        lineup_embed.set_image(url=base_URL)
        sent_message = await interaction.followup.send('**Latest Lineup Card**', embed=lineup_embed)
        lineup_message_id = sent_message.id
        
        next_game_date, _, _ = get_game_date(interaction)
        if next_game_date is None:
            return None, None
        game_id = next_game_date.strftime('%m-%d-%Y')

        category_name = interaction.channel.category.name
        season_id = re.sub(r'\s+', '_', category_name).lower()
        image_firebase_database_reference = db.collection(season_id).document('games').collection(game_id).document('Lineup_Cards')

        lineup_doc = db.collection(season_id).document('games').collection(game_id).document('Lineup_Cards').get()

        if not lineup_doc.exists:
            image_firebase_database_reference.set({
                'messageID': int(lineup_message_id)
            })
        else:
            image_firebase_database_reference.update({
                'messageID': int(lineup_message_id)
            })
        return
        