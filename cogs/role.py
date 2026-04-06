import discord
from discord import app_commands
from discord.ext import commands

from utils.decorators import require_guild


class Role(commands.Cog):
    PERMS = { 'administrator'  : True }

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    role = app_commands.Group(
        name='role', description='Commands to manage roles')

    @role.command(name='create', description='Create one or more new roles')
    @app_commands.checks.has_permissions(**PERMS)
    @app_commands.describe(
        name = "Name of the role or roles you'd like to create, "+
               "separated by commas.")
    @require_guild
    async def create(self, interaction: discord.Interaction, name: str):
        guild = interaction.guild

        
