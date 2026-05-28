import discord
from discord import app_commands
from discord.ext import commands

from datetime import datetime



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
            custom_id='time_type_select',
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

        self.submit_button = discord.ui.ActionRow(
            discord.ui.Button(
                custom_id='submit_reminder',
                style=discord.ButtonStyle.success,
                label='Set Reminder'))

        self.absolute_inputs = discord.ui.ActionRow(
            discord.ui.TextInput(
                custom_id='month_select',
                required=True,
                placeholder='MM',
                min_length=2,
                max_length=2),
            discord.ui.TextInput(
                custom_id='day_select',
                required=True,
                placeholder='DD',
                min_length=1,
                max_length=2),
            discord.ui.TextInput(
                custom_id='year_select',
                required=True,
                placeholder='YYYY',
                min_length=4,
                max_length=4),
            discord.ui.TextInput(
                custom_id='time_select',
                required=True,
                placeholder='HHMM (Military Format)',
                min_length=4,
                max_length=4))

        self.relative_inputs = discord.ui.ActionRow(
            discord.ui.TextInput(
                custom_id='years_select',
                required=True,
                placeholder='Years',
                max_length=2),
            discord.ui.TextInput(
                custom_id='months_select',
                required=True,
                placeholder='Months',
                max_length=2),
            discord.ui.TextInput(
                custom_id='days_select',
                required=True,
                placeholder='Days',
                max_length=2),
            discord.ui.TextInput(
                custom_id='hours_select',
                required=True,
                placeholder='Hours',
                max_length=2),
            discord.ui.TextInput(
                custom_id='minutes_select',
                required=True,
                placeholder='Minutes',
                max_length=2))

    async def on_time_type_change(self, interaction: discord.Interaction):
        items_to_remove = [item
                           for item in self.container.children[2:]]
        for item in items_to_remove:
            self.container.remove_item(item)

        if self.time_type.values[0] == 'on':
            self.add_item(self.absolute_inputs)
        elif self.time_type.values[0] == 'in':
            self.add_item(self.relative_inputs)
        else: 
            return
        self.add_item(self.submit_button)

async def setup(bot: commands.Bot):
    await bot.add_cog(Reminder(bot))
