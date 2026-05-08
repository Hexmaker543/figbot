import discord
from discord import app_commands
from discord.ext import commands

from typing import Literal

from utils.parsers import get_comma_list
from utils.role import (
    create_roles_from_list, place_roles_below_anchor, get_role_anchor)


class Role(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot


    role = app_commands.Group(
        name='role', 
        description='Commands to manage roles',
        default_permissions=discord.Permissions(administrator=True))

    # role create command tree
    create = app_commands.Group(
        name='create', 
        description='Commands to create one or more roles')

    role.add_command(create)

        # create fromlist command
    @create.command(
        name='fromlist',
        description='Create one or more roles from a list of names')
    @app_commands.describe(
        names = "The names of the roles you'd like to add",
        anchor_role = "(Optional) Specify an existing role to place the new "+
                      "roles under",
        anchor_position= "(Optional) Specify whether to place the new roles "+
                         "under or above all other existing roles")
    @app_commands.guild_only
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

        await interaction.response.defer(ephemeral=True)

        try: names = get_comma_list(names)
        except ValueError as e:
            await interaction.followup.send(f"Invalid list of commands. [{e}]")

        if anchor_position and anchor_role:
            await interaction.followup.send("Cannot have 2 anchors.")
            return

        anchor = None

        if anchor_position:
            try: anchor = get_role_anchor(interaction.guild, anchor_position)
            except ValueError as e: 
                await interaction.followup.send(e) ; return

        elif anchor_role:
            anchor = discord.utils.get(
                interaction.guild.roles,
                name=anchor_role)
            if anchor is None:
                await interaction.followup.send("Invalid role name.")
                return

        created_roles = await create_roles_from_list(interaction.guild, names)
        if created_roles is None:
            await interaction.followup.send(
                "Error. No roles created.")
            return

        if anchor:
            await place_roles_below_anchor(
                interaction.guild, anchor, created_roles)

        await interaction.followup.send(f"{len(created_roles)} Roles created.")

    # # role list command
    # @role.command(
    #     name='list',
    #     description="Show a list of all roles in this server")
    # @app_commands.guild_only
    # async def list_roles(interaction:discord.Interaction):
    #     pass


async def setup(bot):
    await bot.add_cog(Role(bot))
