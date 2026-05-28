import discord
from asyncio import sleep



async def send_temporary_message(
    destination,
    content: str,
    delay: int = 5,
    ephemeral: bool = True):
    """Send a message and delete it after a delay (in seconds)

    destination can be:
    - discord.Interaction
    - discord.TextChannel
    - discord.User (DM)"""
    if isinstance(destination, discord.Interaction):
        if destination.response.is_done():
            message = await destination.followup.send(
                content,
                ephemeral=ephemeral)
        else:
            message = await destination.response.send_message(
                content,
                ephemeral=ephemeral)
    else:
        message = await destination.send(content)

    await sleep(delay)
    await message.delete()
