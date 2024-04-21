from services.discordStuff import *

@tree.command(name="avatar", description="Get user avatar", guild=GUILD_ID)
async def avatar(interaction: discord.Interaction, member: discord.Member):
    await interaction.response.send_message(member.display_avatar)