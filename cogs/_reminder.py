import discord
from discord import app_commands
from discord.ext import commands



class Reminder(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    reminder = app_commands.Group(
        name='reminder',
        description='Commands to set, remove, and edit reminders',
        default_permissions=discord.Permissions(send_messages=True))

    @reminder.command(
        name='set',
        description='Create a new reminder')
    @app_commands.guild_only
    async def reminder_set(self, interaction: discord.Interaction):
        # Use Modals
        pass
