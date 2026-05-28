import discord
from discord import app_commands
from discord.ext import commands

from datetime import datetime



class Reminder(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.init_commands()

    def init_commands(self):
        self.init_root_command()
        self.init_set_command()
        self.init_delete_command()
        self.init_list_command()

    def init_root_command(self):
        self.reminder = app_commands.Group(
            name='reminder',
            description="Commands to manage reminders",
            default_permissions=discord.Permissions(
            read_message_history=True))
        self.bot.tree.add_command(self.reminder)

    def init_set_command(self):
        @self.reminder.command(
                name='set',
                description="Set a reminder")
        @app_commands.guild_only
        async def reminder_set(interaction: discord.Interaction):
            await interaction.response.send_modal(SetView())

    def init_delete_command(self):
        @self.reminder.command(
            name='delete',
            description="Delete one or more reminders")
        @app_commands.guild_only
        async def reminder_delete(interaction: discord.Interaction):
            await interaction.response.send_modal(DeleteView())

    def init_list_command(self):
        @self.reminder.command(
            name='list',
            description="List your reminders")
        @app_commands.guild_only
        async def reminder_list(interaction: discord.Interaction):
            await interaction.response.send_modal(ListView())

class SetView(discord.ui.View):
    pass

class DeleteView(discord.ui.View):
    pass

class ListView(discord.ui.View):
    pass

async def setup(bot: commands.Bot):
    await bot.add_cog(Reminder(bot))
