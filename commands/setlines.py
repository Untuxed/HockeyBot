from services.discordStuff import *
from utils.imageGenerator import imageGenerator, pullImage

@tree.command(
    name='setlines',
    description='Set lineup from the google sheet, generates lineup card image, responds with lineup card image.',
    guild=GUILD_ID
)
async def setLines(interaction: discord.Interaction):
    Lineup_File_Name = await imageGenerator(interaction)

    if not Lineup_File_Name:
        await interaction.followup.send('Something went wrong, looking into it.')

    Lineup_File_Name, _ = pullImage(interaction)

    if not Lineup_File_Name:
        await interaction.followup.send('Something went wrong, looking into it.')
    else:
        lineup_embed = discord.Embed(title='Lineup Embed Test 1', description='This is a test of the embed system')
        lineup_embed.set_image(url='https://firebasestorage.googleapis.com/v0/b/voodoobot.appspot.com/o/LineupImages%2FlineupWithName_05-01-2024.png?alt=media&token=e19f07b4-da33-4b0a-b4ae-4fb9a143c99a')
        sent_message = await interaction.followup.send('**Latest Lineup Card**', embed=lineup_embed)
        lineup_message_id = sent_message.id
        print(sent_message.id)
        # sent_message = await interaction.followup.send('**Latest Lineup Card**', file=discord.File(fp=Lineup_File_Name))
        