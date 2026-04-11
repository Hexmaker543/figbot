import discord
from typing import Literal


def get_role_anchor(
    guild:discord.Guild,
    anchor_position:Literal["top", "bottom"]) -> discord.Role:
    """Get the role at either the top or bottom of guild role list"""

    if anchor_position.lower() not in ('top', 'bottom'):
        raise ValueError(f"Invalid anchor position: {anchor_position}")

    if anchor_position.lower() == 'top':
        anchor = guild.roles[-1]
    elif anchor_position.lower() == 'bottom':
        anchor = guild.roles[0]

    return anchor

def get_comma_list(list_string: str):
    if not isinstance(list_string, str): raise ValueError(
        "'list_string' must be a string")
    return [item.strip() for item in list_string.split(',')]
