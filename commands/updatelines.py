from services.discordStuff import *
from utils.imageGenerator import imageGenerator, pullImage
from services.firebaseStuff import *

@tree.command(
    name='updatelines',
    description='Updates the lines for the next game.',
    guild=GUILD_ID
)
async def updateLines(interaction: discord.Interaction):
    did_write_file = await imageGenerator(interaction)

    if not did_write_file:
        await interaction.followup.send('Something went wrong, looking into it.')

    base_URL, _, line_message_id = pullImage(interaction)

    if line_message_id is None:
        await interaction.followup.send('There is not a current lineup set.')
    else:
        lineup_embed = discord.Embed(title='Lineup Embed Test 1', description='This is a test of updating embeds by message ID')
        lineup_embed.set_image(url=base_URL)
        
        Channel = interaction.channel
        lineup_message = await Channel.fetch_message(line_message_id)

        await lineup_message.edit(embed=lineup_embed)
        await interaction.followup.send('updated lineup', ephemeral=True)


    return 