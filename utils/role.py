import discord

import webcolors
from typing import Literal


color_names = webcolors.names(spec='css3')

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

async def place_roles_below_anchor(
    guild:discord.Guild,
    anchor_role:discord.Role,
    roles:list[discord.Role]) -> None:
    """
    Moves the given roles below the anchor role in the role heirarchy
    of the server
    """

    pos = anchor_role.position
    positions: dict[discord.Role, int] = {}

    for role in reversed(roles):
        positions[role] = pos
        pos -= 1

    await guild.edit_role_positions(positions=positions)

async def create_roles_from_list(
    guild:discord.Guild,
    roles:list[str]) -> list[discord.Role]:
    """
    Creates roles from a list of role names and returns them in the order
    they were created
    """

    created_roles = []
    for role in roles:
        new_role = await guild.create_role(name=role)
        created_roles.append(new_role)

    return created_roles

def get_color_roles(guild:discord.Guild) -> list[discord.Role]:
    """Get list of existing color roles"""
    color_roles = []
    for role in guild.roles:
        if role.name in color_names: color_roles.append(role)
    return color_roles

async def remove_color_roles(interaction:discord.Interaction):
    """Remove all of a users color roles"""
    color_roles = get_color_roles(interaction.guild)
    if not color_roles: return
    await interaction.user.remove_roles(*color_roles)

async def delete_empty_color_roles(guild:discord.Guild):
    """Delete all color roles that have no members"""

    color_roles = get_color_roles(guild)
    if not color_roles: return
    for role in color_roles:
        if len(role.members) == 0: await role.delete()

def get_role(guild:discord.Guild, role_name:str) -> discord.Role:
    """Get a role object using a guild object and role name"""
    role = discord.utils.get(guild.roles, name=role_name)
    if role is None: raise ValueError("No role exists with that name.")
    return role

async def ensure_role(guild:discord.Guild, role_name:str):
    try: role = get_role(guild, role_name)
    except ValueError:
        created_roles = await create_roles_from_list(guild, [role_name])
        await place_roles_below_anchor(guild, guild.me.top_role, created_roles)

async def set_role_color(
    guild:discord.Guild,
    role_name:str, 
    rgb_value:tuple[int,int,int]):
    """Sets the color of a role"""

    try: role = get_role(guild, role_name)
    except ValueError as e: 
        raise ValueError(f"Failed to get role '{role_name}'") from e

    try: await role.edit(color=rgb_value)
    except ValueError:
        raise ValueError(f"Failed to change color of role '{role_name}'")

async def create_color_role(
    guild:discord.Guild,
    name:str,
    rgb_value:tuple[int, int, int],
    anchor_role_name:str) -> discord.Role:
    """Creates a color role"""

    r, g, b = rgb_value[0], rgb_value[1], rgb_value[2]
    color = discord.Color.from_rgb(r, g, b)

    new_role = await guild.create_role(name=name, color=color)

    anchor_role = discord.utils.get(guild.roles, name=anchor_role_name)
    if anchor_role is None: return

    await place_roles_below_anchor(guild, anchor_role=anchor_role, roles=[new_role])

    return new_role
