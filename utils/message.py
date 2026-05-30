import discord
from asyncio import sleep



async def send_temporary_message(
    interaction,
    content: str = "You aren't supposed to see this.",
    delay: int = 0,
    ephemeral: bool = True):
    """Send a message and delete it after a delay (in seconds)

    interaction can be:
    - discord.Interaction
    - discord.TextChannel
    - discord.User (DM)"""
    if isinstance(interaction, discord.Interaction):
        if interaction.response.is_done():
            message = await interaction.followup.send(
                content,
                ephemeral=ephemeral)
        else:
            message = await interaction.response.send_message(
                content,
                ephemeral=ephemeral,
                delete_after=delay)
            return
    else:
        message = await interaction.send(content)

    await sleep(delay)
    await message.delete()
