import discord
from discord import app_commands
from discord.ext import commands

import webcolors

from config import COLOR_UNDER_ROLE
from utils.role import (
        remove_color_roles,
        delete_empty_color_roles,
        create_color_role,
        ensure_role)


class Color(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    color = app_commands.Group(
        name='color',
        description="Commands to manage the color of your name",
        default_permissions=discord.Permissions(send_messages=True))

    # color set command
    @color.command(
        name='set',
        description="Set the color of your name")
    @app_commands.describe(
        color_name="Name of the color you want your name to appear with. " +
                   "Leave blank to reset color to default")
    @app_commands.guild_only
    async def set_color(
            self, interaction:discord.Interaction, 
            color_name: str|None=None):

        await interaction.response.defer(ephemeral=True)

        if color_name is None:
            await ensure_role(interaction.guild, COLOR_UNDER_ROLE)
            await remove_color_roles(interaction)
            await delete_empty_color_roles(interaction.guild)
            await interaction.followup.send("You are now colorless!")
            return

        try: rgb = webcolors.name_to_rgb(color_name)
        except ValueError:
            await interaction.followup.send(
                "Invalid color name, check the color list to make sure it " +
                "exists and is spelled correctly.")
            return

        await ensure_role(interaction.guild, COLOR_UNDER_ROLE)
        await remove_color_roles(interaction)
        await delete_empty_color_roles(interaction.guild)

        color_role = await create_color_role(
            interaction.guild, color_name, rgb, COLOR_UNDER_ROLE)

        await interaction.user.add_roles(color_role)
        await interaction.followup.send(f"You are now {color_name}!")

    # color list command
    @color.command(
        name='list',
        description="List all available colors")
    @app_commands.default_permissions(administrator=True)
    @app_commands.guild_only
    async def list_colors(interaction:discord.Interaction):

        await interaction.response.defer(ephemeral=True)

        color_dict: dict[str, tuple[int, int, int]] = {}
        for name in webcolors.names(spec='css3'):
            color_dict[name] = tuple(webcolors.name_to_rgb(name=name))

        try:
            swatches = Swatches(color_dict)
            swatches.send(interaction)
        except Exception as e:
            await interaction.followup.send(f"Error: {e}")
            return

        msg = await interaction.followup.send("")
        await msg.delete()


async def setup(bot):
    await bot.add_cog(Color(bot))
