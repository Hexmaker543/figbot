import discord
from typing import Literal


async def get_role_anchor(
    interaction:discord.Interaction,
    anchor_position:Literal["top", "bottom"]):

    if anchor_position.lower() not in ('top', 'bottom'):
        raise ValueError(f"Invalid anchor position: {anchor_position}")

    if anchor_position.lower() == 'top':
        anchor = interaction.guild.roles[-1]
    elif anchor_position.lower() == 'bottom':
        anchor = interaction.guild.roles[0]

    return anchor
