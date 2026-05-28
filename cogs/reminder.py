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
        await interaction.response.send_message(
            view=ReminderLayout(self.bot),
            ephemeral=True)

class ReminderLayout(discord.ui.LayoutView):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot

        self.time_type = discord.ui.Select(
            required=True,
            placeholder='Select One',
            options=[
                discord.SelectOption(label='on', value='on'),
                discord.SelectOption(label='in', value='in')])
        self.time_type.callback = self.on_time_type_change

        self.container = discord.ui.Container(
            discord.ui.TextDisplay('#Set a Reminder'),
            discord.ui.TextDisplay('Remind me '),
            discord.ui.ActionRow(self.time_type))

async def setup(bot: commands.Bot):
    await bot.add_cog(Reminder(bot))
