import discord
from discord import app_commands
from discord.ext import commands

from typing import Literal

from utils.decorators import require_guild


class Role(commands.Cog):
    PERMS = { 'administrator'  : True }

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
        names: list[str],
        anchor_role: discord.Role = None,
        anchor_position: Literal["top", "bottom"] = None):

        if anchor_position and anchor_role:
            await interaction.followup.send("Cannot have 2 anchors.")
            return

        if anchor_role:
            anchor = discord.utils.get(
                interaction.guild.roles,
                name=anchor_role)
            if anchor is None:
                await interaction.followup.send(
                    f"{anchor_role} is not a valid anchor role.")
                return
        elif anchor_position:
            if anchor_position.lower() == 'top':
            elif anchor_position.lower() == 'bottom':
            else:
                await interaction.followup.send(
                    f"{anchor_position} is not a valid anchor position. "+
                    "Valid anchor positions are 'top' and 'bottom'")
                return
