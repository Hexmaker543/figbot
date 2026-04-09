import discord
from discord import app_commands
from discord.ext import commands

from typing import Literal

from utils.decorators import require_guild
from utils.parsers import get_comma_list, get_role_anchor 
from utils.role import create_roles_from_list, place_roles_below_anchor


class Role(commands.Cog):
    PERMS = { 'administrator' : True }

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    role = app_commands.Group(
        name='role', 
        description='Commands to manage roles')

    create = app_commands.Group(
        name='create', 
        description='Commands to create one or more roles')

    role.add_command(create)

    @create.command(
        name='fromlist',
        description='Create one or more roles from a list of names')
    @app_commands.checks.has_permissions(**PERMS)
    @app_commands.describe(
        names = "The names of the roles you'd like to add",
        anchor_role = "(Optional) Specify an existing role to place the new "+
                      "roles under",
        anchor_position= "(Optional) Specify whether to place the new roles "+
                         "under or above all other existing roles")
    @require_guild
    async def create_fromlist(
        self,
        interaction: discord.Interaction,
        names: str,
        anchor_role: discord.Role = None,
        anchor_position: Literal["top", "bottom"] = None):
        """
        Slash command that allows the user to create roles from a list of
        role names
        """

        try: names = get_comma_list(names)
        except ValueError as e:
            await interaction.followup.send("Invalid list of commands.")

        await interaction.response.defer(ephemeral=True)

        if anchor_position and anchor_role:
            await interaction.followup.send("Cannot have 2 anchors.")
            return

        try: anchor = get_role_anchor(interaction.guild, anchor_position)
        except ValueError as e: 
            await interaction.followup.send(e) ; return

        created_roles = await create_roles_from_list(interaction.guild, names)
        if created_roles is None:
            await interaction.followup.send(
                "Error. No roles created.")
            return

        await place_roles_below_anchor(
            interaction.guild, anchor, created_roles)
