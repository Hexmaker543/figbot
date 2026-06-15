from typing import Literal

import discord
from discord import app_commands
from discord.ext import commands

from datetime import datetime
from dateutil import parser
from dateutil.relativedelta import relativedelta

from utils.data import ensure_database, get_connection
from utils.parsers import get_comma_list
from utils.ui import get_text_from_modal
from utils.message import send_temporary_message


class ReminderManager:
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        ensure_database()

    def save_reminder(self,
        user_id: int,
        name: str,
        datetime: datetime,
        channel_id: int,
        description: str = None,
        repeat_key: str | None = None):
        conn = get_connection()
        cursor = conn.cursor()
        datetime = datetime.isoformat()
        cursor.execute("""
        INSERT INTO reminders (
            user_id,
            name,
            description,
            datetime,
            repeat_key,
            channel_id
        )
        VALUES (?,?,?,?,?,?)""", (user_id, name, description,
                                datetime, repeat_key, channel_id))
        conn.commit()
        conn.close()

    def get_reminders(self,
        user_id:int|None=None) -> dict:
        conn = get_connection()
        cursor = conn.cursor()
        if user_id is None: cursor.execute('SELECT * FROM reminders')
        else:
            cursor.execute('SELECT * FROM reminders WHERE user_id = ?',
                           (user_id,))
        reminder_tuples = cursor.fetchall()
        conn.close()
        reminders = []
        for tup in reminder_tuples:
            reminders.append({
                'user_id' : tup[0],
                'name' : tup[1],
                'description' : tup[2],
                'datetime' : datetime.fromisoformat(tup[3]),
                'repeat_key' : tup[4],
                'channel_id' : tup[5]
            })
        return reminders

    def trigger_reminder(self, reminder:dict):
        user_id = reminder['user_id']
        name = reminder['name']
        description = reminder['description']
        datetime = reminder['datetime']
        repeat_key = reminder['repeat_key']
        channel_id = reminder['channel_id']

        channel = self.bot.get_channel(channel_id)
        user = self.bot.get_user(user_id)

        msg = f'{user.mention} Reminder: {name}'
        if description: msg += f' - {description}'

        channel.send(f'{user.mention} Reminder: {name}')

    def check_reminders(self):
        reminders = self.get_reminders()
        for reminder in reminders:
            reminder_datetime = datetime.fromisoformat(reminder['datetime'])
            if reminder_datetime >= datetime.now:
                self.trigger_reminder(reminder)

    def adjust_loop_timer(self):
        pass


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
            await interaction.response.send_message(
                view=SetView(interaction, self.bot),
                ephemeral=True)

    def init_delete_command(self):
        @self.reminder.command(
            name='delete',
            description="Delete one or more reminders")
        @app_commands.guild_only
        async def reminder_delete(interaction: discord.Interaction):
            await interaction.response.send_message(
                view=DeleteView(interaction),
                ephemeral=True)

    def init_list_command(self):
        @self.reminder.command(
            name='list',
            description="List your reminders")
        @app_commands.guild_only
        async def reminder_list(interaction: discord.Interaction):
            await interaction.response.send_message(
                view=ListView(interaction),
                ephemeral=True)


class SetView(discord.ui.LayoutView):
    def __init__(self, interaction: discord.Interaction, bot: commands.Bot):
        super().__init__()

        self.original_interaction = interaction

        self.reminder_manager = ReminderManager(bot)

        self.current_time = datetime.now().strftime("%m-%d-%Y %H:%M:%S")
        self.DEFAULT_REMINDER_NAME = f'Reminder {self.current_time}'
        self.DEFAULT_REMINDER_DESC = None

        self.reminder_name = self.DEFAULT_REMINDER_NAME
        self.reminder_desc = self.DEFAULT_REMINDER_DESC

        self._reset_datetime()
        self.time_type: Literal['absolute', 'relative', None] = None
        self.repeat_key: str | None = None
        self.repeater_error = None
        self.is_disabled = {'absolute' : False, 'relative' : False}

        self._build_ui()

    def _build_ui(self):
        self.container = discord.ui.Container()
        self.container.add_item(discord.ui.TextDisplay(
            "# Set a Reminder"))
        self.container.add_item(discord.ui.Separator(
            spacing=discord.SeparatorSpacing.large))
        self._add_name_and_desc()
        self._add_time_buttons()
        self._add_absolute_input()
        self._add_relative_input()
        self._add_reminder_repeater()
        self.add_item(self.container)

    async def _refresh_display(self):
        self.container = discord.ui.Container()
        self.clear_items()
        self._build_ui()
        await self.original_interaction.edit_original_response(view=self)

    def _reset_datetime(self):
        self.datetime_parser_error = None
        self.datetime_string = None
        self.reminder_datetime = None
        self.relativedelta_error = None
        self.relativedelta_string = None

    def _add_name_and_desc(self):
        self.container.add_item(discord.ui.TextDisplay(
            "### Set a name and description (Optional)."))

        def update_name_or_desc(input: str, type: Literal['name', 'desc']):
            if input:
                if type == 'name': self.reminder_name = input
                if type == 'desc': self.reminder_desc = input
            else:
                if type == 'name':
                    self.reminder_name = self.DEFAULT_REMINDER_NAME
                if type == 'desc':
                    self.reminder_desc = self.DEFAULT_REMINDER_DESC

        async def on_name_button(interaction: discord.Interaction):
            name = await get_text_from_modal(
                interaction,
                title='Set Reminder Name',
                label='Give your reminder a name (Optional).',
                placeholder='(16 Character Limit)',
                max_length=16)
            update_name_or_desc(name, 'name')
            await self._refresh_display()

        async def on_desc_button(interaction: discord.Interaction):
            desc = await get_text_from_modal(
                interaction,
                title='Set Description',
                label='Enter a short description (Optional).',
                placeholder='(200 Character Limit)',
                max_length=200,
                style=discord.TextStyle.long)
            update_name_or_desc(desc, 'desc')
            await self._refresh_display()

        name_button = discord.ui.Button(label='Set Name')
        desc_button = discord.ui.Button(label='Set Description')
        name_button.callback = on_name_button
        desc_button.callback = on_desc_button

        self.container.add_item(discord.ui.ActionRow(name_button, desc_button))
        self.container.add_item(discord.ui.TextDisplay(
            content=f'**Name:** {self.reminder_name}'))
        if self.reminder_desc:
            self.container.add_item(discord.ui.TextDisplay(
                content=f'**Description:** {self.reminder_desc}'))
        self.container.add_item(discord.ui.Separator(
            spacing=discord.SeparatorSpacing.large))

    def _add_time_buttons(self):
        self.container.add_item(discord.ui.TextDisplay(
            "### What type of reminder would you like to set?"))
        if not any(self.is_disabled.values()):
            self.container.add_item(discord.ui.TextDisplay(
                "\n\n__Absolute:__ January 1st, 2003 at 08:00 AM\n\n" +
                "__Relative:__ In 2 days, 3 hours, and 5 minutes."))

        absolute_button = discord.ui.Button(label='Absolute')
        relative_button = discord.ui.Button(label='Relative')

        absolute_button.disabled = self.is_disabled['absolute']
        relative_button.disabled = self.is_disabled['relative']

        async def set_absolute(interaction):
            self.time_type = 'absolute'
            self.is_disabled['absolute'] = True
            self.is_disabled['relative'] = False
            await self._refresh_display()
            await send_temporary_message(interaction)

        async def set_relative(interaction):
            self.time_type = 'relative'
            self.is_disabled['absolute'] = False
            self.is_disabled['relative'] = True
            await self._refresh_display()
            await send_temporary_message(interaction)

        absolute_button.callback = set_absolute
        relative_button.callback = set_relative

        self.container.add_item(discord.ui.ActionRow(
            absolute_button,
            relative_button))

    def _add_absolute_input(self):
        if self.time_type != 'absolute': return

        async def on_datetime_button(interaction: discord.Interaction):
            user_datetime = await get_text_from_modal(
                interaction=interaction,
                title='Set Date',
                label='Set the date',
                placeholder='MM-DD-YYYY HH:MM',
                required=True)
            try: self.reminder_datetime = parser.parse(user_datetime)
            except (parser.ParserError, ValueError, TypeError) as e:
                self.datetime_parser_error = f'{e}'
            if not isinstance(self.reminder_datetime, datetime):
                self.datetime_parser_error = (
                    f"You really thought '{user_datetime}' was gonna work?\n"+
                    "Try to match the syntax you see in the form.")
                await self._refresh_display()
                self._reset_datetime()
                return
            self.datetime_string = self.reminder_datetime.strftime(
                "%A, %B %d, %Y at %I:%M %p")
            self.relativedelta_string = relativedelta(
                self.datetime_string, self.current_time)
            await self._refresh_display()

        datetime_button = discord.ui.Button(label='Set Date and Time')
        datetime_button.callback = on_datetime_button
        self.container.add_item(discord.ui.ActionRow(datetime_button))

        if self.datetime_string:
            self.container.add_item(discord.ui.TextDisplay(
                f'**Absolute:** {self.datetime_string}\n'+
                f'*In ({self.relativedelta_string})*'))

        if self.datetime_parser_error:
            self.container.add_item(discord.ui.TextDisplay(
                self.datetime_parser_error))
            self._reset_datetime()

    def _add_relative_input(self):
        if self.time_type != 'relative': return

        modal = discord.ui.Modal(title="Set Timer")

        months_input = discord.ui.TextInput(
            label="Months",
            placeholder="0",
            required=False,
            max_length=2)
        weeks_input = discord.ui.TextInput(
            label="Weeks", placeholder="0",
            required=False,
            max_length=2)
        days_input = discord.ui.TextInput(
            label="Days",
            placeholder="0",
            required=False,
            max_length=3)
        hours_input = discord.ui.TextInput(
            label="Hours",
            placeholder="0",
            required=False,
            max_length=3)
        minutes_input = discord.ui.TextInput(
            label="Minutes",
            placeholder="0",
            required=False,
            max_length=3)

        modal.add_item(months_input)
        modal.add_item(weeks_input)
        modal.add_item(days_input)
        modal.add_item(hours_input)
        modal.add_item(minutes_input)

        async def on_submit(interaction: discord.Interaction):
            try:
                self.relativedelta_string = (
                    f'{int(months_input.value or 0)} months, '+
                    f'{int(weeks_input.value or 0)} weeks, '+
                    f'{int(days_input.value or 0)} days, '+
                    f'{int(hours_input.value or 0)} hours, '+
                    f'and {int(minutes_input.value or 0)} minutes')

                delta = relativedelta(
                    months=int(months_input.value or 0),
                    weeks=int(weeks_input.value or 0),
                    days=int(days_input.value or 0),
                    hours=int(hours_input.value or 0),
                    minutes=int(minutes_input.value or 0))

                self.reminder_datetime = datetime.now() + delta
                self.datetime_string = self.reminder_datetime.strftime(
                    "%A, %B %d, %Y at %I:%M %p")
            except (ValueError, TypeError) as e:
                self.relativedelta_error = f'{e}'
            await send_temporary_message(interaction)
            await self._refresh_display()

        async def on_timer_button(interaction: discord.Interaction):
            modal.on_submit = on_submit
            await interaction.response.send_modal(modal)

        timer_button = discord.ui.Button(label='Set Timer')
        timer_button.callback = on_timer_button
        self.container.add_item(discord.ui.ActionRow(timer_button))

        if self.relativedelta_string:
            self.container.add_item(discord.ui.TextDisplay(
                f'**Relative:** {self.relativedelta_string}\n'+
                f'*(On {self.datetime_string})*'))

        if self.relativedelta_error:
            self.container.add_item(discord.ui.TextDisplay(
                self.relativedelta_error))
            self._reset_datetime()

        self.container.add_item(discord.ui.Separator(
            spacing=discord.SeparatorSpacing.large))

    def _add_reminder_repeater(self):
        if not self.reminder_datetime: return

        self.container.add_item(discord.ui.TextDisplay(
            "### How would you like this reminder?\n"+
            "• **Enable Repeater** — Remind me regularly\n"+
            "• **Set Reminder** — One-time reminder"))

        # Repeat Modal
        repeater_modal = discord.ui.Modal(title='Setup a Repeating Reminder')
        repeater_modal.add_item(discord.ui.TextDisplay("Repeat Every:"))
        years_input = discord.ui.Label(
            text='Years',
            component=discord.ui.TextInput(
                placeholder="0",
                required=False,
                max_length=1))
        months_input = discord.ui.Label(
            text='Months',
            component=discord.ui.TextInput(
                placeholder="0",
                required=False,
                max_length=2))
        weeks_input = discord.ui.Label(
            text='Weeks',
            component=discord.ui.TextInput(
                placeholder="0",
                required=False,
                max_length=2))
        days_input = discord.ui.Label(
            text='Days',
            component=discord.ui.TextInput(
                placeholder="0",
                required=False,
                max_length=3))
        hours_input = discord.ui.Label(
            text='Hours',
            component=discord.ui.TextInput(
                placeholder="0",
                required=False,
                max_length=3))
        minutes_input = discord.ui.Label(
            text='Minutes',
            component=discord.ui.TextInput(
                placeholder="0",
                required=False,
                max_length=4))
        repeats_input = discord.ui.Label(
            text="Times to Repeat:",
            description="Type in how many times you want the reminder to " +
                "repeat, or type '0' to make it indefinite.",
            component=discord.ui.TextInput(
                placeholder="0",
                max_length=4))

        async def on_submit(interaction: discord.Interaction):
            try:
                years = int(years_input.component.value or 0)
                months = int(months_input.component.value or 0)
                weeks = int(weeks_input.component.value or 0)
                days = int(days_input.component.value or 0)
                hours = int(hours_input.component.value or 0)
                minutes = int(minutes_input.component.value or 0)
                repeats = int(repeats_input.component.value or 0)

                self.repeat_key = (f'{years},{months},{weeks},{days},' +
                                  f'{hours},{minutes},{repeats}')

            except (ValueError, TypeError) as e:
                self.repeater_error = f'{e}'
                await send_temporary_message(interaction)

        async def on_repeater_button(interaction: discord.Interaction):
            repeater_modal.on_submit = on_submit
            await interaction.response.send_modal(repeater_modal)
            self._refresh_display()


        def get_keys():
            keys = get_comma_list(self.repeat_key)
            keys_dict = {
                'years' : keys[0],
                'months' : keys[1],
                'weeks' : keys[2],
                'days' : keys[3],
                'hours' : keys[4],
                'minutes' : keys[5],
                'repeats' : keys[6]
            }
            return keys_dict

        # Submit Modal
        submit_modal = discord.ui.Modal(title='Set Reminder')
        submit_modal.add_item(
            discord.ui.TextDisplay("Please Review Your Reminder")
        )

        submit_modal.add_item(
            discord.ui.TextDisplay(f"Name: {self.reminder_name}")
        )
        submit_modal.add_item(
            discord.ui.TextDisplay(f"Description: {self.reminder_desc}")
        )
        submit_modal.add_item(
            discord.ui.TextDisplay(f"Datetime: {self.datetime_string}")
        )

        keys = get_keys()
        submit_modal.add_item(
            discord.ui.TextDisplay(
f"""Repeats every:
Years: {keys['years']}
Months: {keys['months']}
Weeks: {keys['weeks']}
Days:  {keys['days']}
Hours: {keys['hours']}
Minutes:{keys['minutes']}

It will repeat {keys['repeats']} times"""))

        async def on_submit(interaction: discord.Interaction):
            interaction.response.defer(ephemeral=True)
            try:
                user_id = interaction.user.id
                name = self.reminder_name
                desc = self.reminder_desc
                datetime = self.reminder_datetime.isoformat()
                repeat_key = self.repeat_key
                channel_id = interaction.channel_id

                self.reminder_manager.save_reminder(
                    user_id=user_id,
                    name=name,
                    datetime=datetime,
                    channel_id=channel_id,
                    description=desc,
                    repeat_key=repeat_key,
                )

                send_temporary_message(interaction, 'Reminder set.', 5)
            except Exception as e:
                interaction.followup.send(f"Error. Please alert admins. [{e}]")

        async def on_submit_button(interaction: discord.Interaction):
            submit_modal.on_submit = on_submit
            await interaction.response.send_modal(submit_modal)
            self._refresh_display()

        repeater_button = discord.ui.Button(label='Enable Repeater')
        submit_button = discord.ui.Button(label='Set Reminder')
        repeater_button.callback = on_repeater_button()
        submit_button.callback = on_submit_button()
        self.container.add_item(
            discord.ui.ActionRow(repeater_button, submit_button)
        )


class DeleteView(discord.ui.View):
    def __init__(self, interaction: discord.Interaction):
        super().__init__()

        self.original_interaction = interaction


class ListView(discord.ui.View):
    def __init__(self, interaction: discord.Interaction):
        super().__init__()

        self.original_interaction = interaction


async def setup(bot: commands.Bot):
    await bot.add_cog(Reminder(bot))
