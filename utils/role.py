import discord


async def place_roles_below_anchor(
    guild:discord.Guild,
    anchor_role:discord.Role,
    roles:list[discord.Role]) -> None:
    """
    Moves the given roles below the anchor role in the role heirarchy
    of the server
    """

    pos = anchor_role.position - 1
    positions = dict[discord.Role, int] = {}

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
