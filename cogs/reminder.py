import discord
from discord import app_commands
from discord.ext import commands

from datetime import datetime
from dateutil.relativedelta import relativedelta

from utils.parsers import extract_value
from utils.data import *
from utils.message import send_temporary_message



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

        self.container = discord.ui.Container(
            discord.ui.TextDisplay('#Set a Reminder'),
            discord.ui.TextDisplay('Remind me '))

        self.name_and_desc = discord.ui.ActionRow(
            discord.ui.TextInput(
                required=False,
                placeholder='Name',
                min_length=3,
                max_length=16),
            discord.ui.TextInput(
                required=False,
                placeholder='Short description (200 Char Limit)',
                style=discord.TextStyle.long))

        self.time_type = discord.ui.ActionRow(
            discord.ui.Select(
                custom_id='time_type_select',
                required=True,
                placeholder='Select One',
                options=[
                    discord.SelectOption(label='on', value='on'),
                    discord.SelectOption(label='in', value='in')]))
        self.time_type.callback = self.on_time_type_change

        self.container.add_item(self.name_and_desc)
        self.container.add_item(self.time_type)
        self.add_item(self.container)

        self.submit_button = discord.ui.ActionRow(
            discord.ui.Button(
                custom_id='submit_reminder',
                style=discord.ButtonStyle.success,
                label='Set Reminder'))
        self.submit_button.callback = self.on_submit

        self.absolute_inputs = discord.ui.ActionRow(
            discord.ui.TextInput(
                label='Date',
                required=True,
                placeholder='MMDDYYYY',
                min_length=8,
                max_length=8),
            discord.ui.TextInput(
                label='Time',
                required=True,
                placeholder='HHMM (Military Format)',
                min_length=4,
                max_length=4))

        self.relative_inputs = discord.ui.ActionRow(
            discord.ui.TextInput(
                label='Date Offset',
                required=True,
                placeholder='XyXmXd (e.g. 1y2m3d)',
                max_length=20),
            discord.ui.TextInput(
                label='Time Offset',
                required=True,
                placeholder='XhXm (e.g. 4h5m)',
                max_length=10))

    async def on_time_type_change(self, interaction: discord.Interaction):
        items_to_remove = [item
                           for item in self.container.children[3:]]
        for item in items_to_remove:
            self.container.remove_item(item)

        if self.time_type.values[0] == 'on':
            self.container.add_item(self.absolute_inputs)
        elif self.time_type.values[0] == 'in':
            self.container.add_item(self.relative_inputs)
        else:
            return
        self.container.add_item(self.submit_button)

        await interaction.response.defer()
        await interaction.edit_original_response(view=self)

    async def on_submit(self, interaction: discord.Interaction):
        reminder_data = load_data('reminders')

        try: reminder_datetime = self.get_datetime()
        except ValueError:
            send_temporary_message(
                interaction,
                "Invalid input, please try again.")

        if reminder_datetime <= datetime.now():
            await send_temporary_message(
                interaction, 
                "I have not figured out time travel in python yet. Try again.")
            return

        user_id = interaction.user.id
        reminder_name = (
            self.name_and_desc.children[0].value
            or f'Reminder {datetime.now().strftime('%Y%m%d_%H%M%S')}')
        reminder_desc = (
            self.name_and_desc.children[1].value 
            or 'No Description')

        reminder_data[user_id] = {
            'name' : reminder_name,
            'desc' : reminder_desc,
            'datetime' : reminder_datetime.isoformat()}

        save_data('reminders', reminder_data)
        send_temporary_message(
            interaction, 
            f"Created reminder '{reminder_name}'")

def get_datetime(self):
    if self.time_type.values[0] == 'on':
        date_input = self.absolute_inputs.children[0].value.strip().replace('-', '').replace('/', '')
        time_input = self.absolute_inputs.children[1].value.strip()

        datetime_string = f'{date_input}{time_input}'
        return datetime.strptime(datetime_string, "%m%d%Y%H%M")

    elif self.time_type.values[0] == 'in':
        date_input = self.relative_inputs.children[0].value.strip().lower()
        time_input = self.relative_inputs.children[1].value.strip().lower()

        years = extract_value(r'(\d+)y', date_input)
        months = extract_value(r'(\d+)mo', date_input)
        days = extract_value(r'(\d+)d', date_input)
        hours = extract_value(r'(\d+)h', time_input)
        minutes = extract_value(r'(\d+)m', time_input)

        future_time = datetime.now() + relativedelta(
            years=years,
            months=months,
            days=days,
            hours=hours,
            minutes=minutes)

        return future_time

async def setup(bot: commands.Bot):
    await bot.add_cog(Reminder(bot))
